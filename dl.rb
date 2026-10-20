#!/usr/bin/env ruby
# Download curated public-domain Ethiopian manuscript images from upload.wikimedia.org
# (no API calls -> no rate limiting) and write a manifest for the reader.
require 'json'
require 'net/http'
require 'uri'
require 'fileutils'

UA = { "User-Agent" => "EOTCBibleReader/1.0 (offline personal reader; educational)" }
OUT = "reader/data/manuscripts"
FileUtils.mkdir_p(OUT)

items = JSON.parse(File.read(ARGV[0] || "/var/folders/6f/rln9mdz94sqg2dq1_zm9hs2w0000gn/T/opencode/sel2.json"))

def get(url)
  uri = URI(url)
  req = Net::HTTP::Get.new(uri); UA.each { |k,v| req[k] = v }
  Net::HTTP.start(uri.host, uri.port, use_ssl: true) { |h| h.request(req) }
end

manifest = []
items.each_with_index do |it, i|
  slug = it["title"].downcase.gsub(/[^a-z0-9]+/, "-").gsub(/^-|-$/, "")[0,70]
  slug += "-#{i}" if slug.empty?
  file = slug + ".jpg"
  dest = File.join(OUT, file)
  unless File.exist?(dest) && File.size(dest) > 1000
    begin
      res = get(it["url"])
      if res.code.to_i == 200
        File.binwrite(dest, res.body)
      else
        warn "\n#{it["url"]} -> #{res.code}"
      end
    rescue => e
      warn "\n#{it["url"]} -> #{e}"
    end
  end
  next unless File.exist?(dest) && File.size(dest) > 1000
  manifest << it.merge("local" => "data/manuscripts/#{file}")
  print "\r#{i+1}/#{items.size} | saved #{manifest.size} "
end
puts

File.write("reader/data/manuscripts.js", "window.__EBMAN=#{manifest.to_json};")
mb = Dir.glob("#{OUT}/*").sum { |f| File.size(f) } / 1024.0 / 1024.0
puts "manifest: #{manifest.size} images, #{'%.1f' % mb} MB"
