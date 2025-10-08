# ///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
require_relative "boot"

lawline

# ▛▞ Token Classification Demo ▞//
puts "Demonstrating token classification:"
# ▞▞//▟

examples = [
  "//▞▞ This is an imprint",
  "SECTION_HEAD marker: Section begins",
  "SECTION_TAIL marker: Section ends",
  "NAMED_SECTION marker: DataProcessor",
  "▞▞ Double colon semantics",
  "//▞ Minor open",
  "Regular text line"
]

# ▛▞ Classification Loop ▞//
examples.each do |ex|
  token_type = classify(ex)
  puts "#{ex.ljust(40)} -> #{token_type}"
  
  if token_type == :NAMED_SECTION
    name = extract_section_name(ex)
    puts "  └─ Section name: #{name}"
  end
end
# ▞▞//▟

# ▛▞ Ruby Syntax Features ▞//
puts "\nRuby Syntax Features:"
puts "- Blocks and iterators"
puts "- Dynamic typing with inference"
puts "- Regex as first-class literals"
# ▞▞//▟
