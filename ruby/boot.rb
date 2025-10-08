# ///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
BANNER = "///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂"

def lawline
  puts BANNER
end

# Token classification system
TOKENS = {
  %r{//▞▞} => :IMPRINT,
  %r{▛///▞} => :SECTION_HEAD,
  %r{▞▞//▟} => :SECTION_TAIL,
  %r{▛▞\s+(.+?)\s+▞//} => :NAMED_SECTION,
  %r{▞▞} => :COLON2,
  %r{//▞} => :OPEN_MINOR,
}

def classify(line)
  TOKENS.each { |rx, tag| return tag if line.match?(rx) }
  :TEXT
end

def extract_section_name(line)
  match = line.match(/▛▞\s+(.+?)\s+▞\/\//)
  match ? match[1] : nil
end
