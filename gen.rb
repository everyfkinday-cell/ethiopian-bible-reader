#!/usr/bin/env ruby
# Parse the cpradmin/ethiopian-bible geez-complete.md (official open-source Ge'ez
# EOTC corpus) into compact per-book JS files for an offline reader.
require 'json'
require 'fileutils'

SRC  = "geez-complete.md"
OUT  = "reader"
DATA = File.join(OUT, "data", "books")
FileUtils.mkdir_p(DATA)

lines = File.readlines(SRC, encoding: "UTF-8")

books = []
cur = nil
chapter = 0
lines.each do |raw|
  line = raw.rstrip

  if line =~ /^title:\s*"(.*)"\s*$/
    cur = { title: $1, slug: nil, section: nil, canon: nil, abbr: nil, chapters: {} }
    books << cur
    next
  end
  next unless cur
  if line =~ /^slug:\s*"(.*)"\s*$/      then cur[:slug]    = $1; next; end
  if line =~ /^section:\s*"(.*)"\s*$/   then cur[:section] = $1; next; end
  if line =~ /^canon_number:\s*(\d+)/   then cur[:canon]   = $1.to_i; next; end
  if line =~ /^iam_abbrev:\s*"(.*)"/    then cur[:abbr]    = $1; next; end

  if line =~ /^## Chapter (\d+)/
    chapter = $1.to_i
    cur[:chapters][chapter] = []
    next
  end
  if line =~ /^\*\*(\d+)\*\*\s*(.*)$/
    vnum = $1.to_i
    text = $2.gsub(/\s+/, " ").strip
    cur[:chapters][chapter] ||= []
    cur[:chapters][chapter] << [vnum, text]
  end
end

SECTION_ORDER = ["Torah (Orit)","Historical","Wisdom","Prophets",
  "Deuterocanonical","Unique to Ethiopia","New Testament","New Testament (Ethiopian)"]
books.sort_by! { |b| b[:canon] || 999 }

meta = []
books.each do |b|
  chs = b[:chapters].sort.map do |num, vs|
    vs.sort_by! { |n,_| n }
    [num, vs]
  end
  next if chs.empty?
  abbr = b[:abbr] || b[:slug]
  payload = "#{abbr.to_json}:#{chs.to_json}"
  File.write(File.join(DATA, "#{abbr}.js"),
             "window.__EB=window.__EB||{};window.__EB[#{abbr.to_json}]=#{chs.to_json};")
  meta << {
    "abbr" => abbr, "name" => b[:title], "slug" => b[:slug],
    "section" => b[:section], "canon" => b[:canon],
    "chapters" => chs.size, "verses" => chs.sum { |_,v| v.size }
  }
end

File.write(File.join(OUT, "data", "meta.js"), "window.__EBM=#{meta.to_json};")
puts "books=#{meta.size} chapters=#{meta.sum{|m|m['chapters']}} verses=#{meta.sum{|m|m['verses']}}"
meta.each { |m| printf "%-6s %-26s %-22s ch=%-4d v=%d\n", m["abbr"], m["name"], m["section"], m["chapters"], m["verses"] }
