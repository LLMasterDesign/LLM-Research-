// ///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
use lawline::{lawline, Tokens, BANNER};

fn main() {
    lawline();
    println!("Banner constant: {}", BANNER);
    
    // Demonstrate token classification
    let tokens = Tokens::new();
    let examples = vec![
        "//▞▞ This is an imprint",
        "SECTION_HEAD marker",
        "SECTION_TAIL marker",
        "NAMED_SECTION marker",
        "▞▞ Double colon semantics",
        "//▞ Minor open",
        "Regular text line",
    ];
    
    println!("\n▛▞ Token Classification Examples ▞//");
    for example in examples {
        println!("{:20} -> {}", example, tokens.classify(example));
    }
    println!("▞▞//▟");
}
