#!/usr/bin/env ruby
# Downloads public-domain Ethiopian Bible / Gospel manuscript images from
# Wikimedia Commons into reader/data/manuscripts and writes a manifest.
require 'json'
require 'net/http'
require 'uri'
require 'fileutils'

UA = { "User-Agent" => "EOTCBibleReader/1.0 (offline personal reader; educational)" }
OUT = "reader/data/manuscripts"
FileUtils.mkdir_p(OUT)

def api(params)
  uri = URI("https://commons.wikimedia.org/w/api.php")
  uri.query = URI.encode_www_form(params)
  req = Net::HTTP::Get.new(uri); UA.each { |k,v| req[k] = v }
  res = Net::HTTP.start(uri.host, uri.port, use_ssl: true) { |h| h.request(req) }
  8.times { |i| break unless res.code.to_i == 429; sleep(6*(i+1));
    res = Net::HTTP.start(uri.host, uri.port, use_ssl: true) { |h| h.request(req) } }
  JSON.parse(res.body)
end

# Curated, Bible/Gospel-relevant categories
CATS = [
  "Category:Garima Gospels",
  "Category:Ethiopian manuscripts"
]

titles = []
CATS.each do |c|
  r = api({ action: "query", list: "categorymembers", cmtitle: c,
            cmtype: "file", cmlimit: "200", format: "json" })
  titles.concat((r.dig("query","categorymembers") || []).map { |m| m["title"] })
  sleep 1
end
titles.uniq!

# Curate: keep Garima always, and Bible/Gospel/manuscript-illumination items
KEEP = /\b(garima|bibl|gospel|testament|psalt|ethiopic|ethiopian bible|
  manuscript|codex|illuminat|apostle|virgin|christ|evangel|parchment)/xi
DROP = /(mosque|museum building|book cover|cover\.jpg|monk|portrait of|
  church building|landscape|photo of)/xi
sel = titles.select { |t| t =~ KEEP && t !~ DROP }

records = []
sel.each_slice(25).with_index do |batch, i|
  r = api({ action: "query", titles: batch.join("|"), prop: "imageinfo",
            iiprop: "url|size|extmetadata|user", iiurlwidth: "1000", format: "json" })
  (r.dig("query","pages") || {}).each_value do |p|
    ii = p["imageinfo"]&.first; next unless ii
    em = ii["extmetadata"] || {}
    clean = ->(v){ v.to_s.gsub(/<[^>]+>/," ").gsub(/\s+/," ").strip }
    records << {
      "title"   => p["title"].sub(/\AFile:/, "").sub(/\.(jpg|jpeg|png|JPG)\z/i, ""),
      "file"    => p["title"].sub(/\AFile:/, "").sub(/\.(jpg|jpeg|png|JPG)\z/i, "").gsub(/[^A-Za-z0-9]+/,"-").downcase + ".jpg",
      "thumb"   => ii["thumburl"],
      "page"    => "https://commons.wikimedia.org/wiki/" + URI.encode_www_form_component(p["title"]),
      "w"       => ii["width"], "h" => ii["height"],
      "license" => clean.call(em.dig("LicenseShortName","value")),
      "artist"  => clean.call(em.dig("Artist","value")),
      "credit"  => clean.call(em.dig("Credit","value")),
      "desc"    => clean.call(em.dig("ImageDescription","value"))[0,300]
    }
  end
  sleep 2
end

# rank: Garima first, then Gospels/illuminated
records.sort_by! do |r|
  t = r["title"].downcase
  [ (t.include?("garima") ? 0 : t =~ /gospel|bibl/ ? 1 : 2), t ]
end

def download(url, path)
  uri = URI(url)
  req = Net::HTTP::Get.new(uri); UA.each { |k,v| req[k] = v }
  res = Net::HTTP.start(uri.host, uri.port, use_ssl: true) { |h| h.request(req) }
  6.times { |i| break unless res.code.to_i == 429; sleep(5*(i+1));
    res = Net::HTTP.start(uri.host, uri.port, use_ssl: true) { |h| h.request(req) } }
  return false unless res.code.to_i == 200
  File.binwrite(path, res.body)
  true
end

ok = 0
records.each_with_index do |r, i|
  dest = File.join(OUT, r["file"])
  unless File.exist?(dest) && File.size(dest) > 1000
    begin
      ok += 1 if download(r["thumb"], dest)
    rescue => e
      warn "dl fail #{r["title"]}: #{e}"
    end
    sleep 0.4
  else
    ok += 1
  end
  print "\r#{i+1}/#{records.size} images (#{ok} ok) "
end
puts

manifest = records.map { |r| r.merge("local" => "data/manuscripts/" + r["file"]) }
File.write("reader/data/manuscripts.js", "window.__EBMAN=#{manifest.to_json};")
puts "manifest: #{manifest.size} items, downloaded/verified #{ok}"
puts "size: #{Dir.glob("#{OUT}/*").sum { |f| File.size(f) } / 1024 / 1024} MB"
