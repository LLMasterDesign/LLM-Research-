// ///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂
// Token analysis tool for mathematical notation

use std::collections::HashMap;

fn main() {
    println!("///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂");
    println!("Token Analysis Tool\n");

    // Symbol analysis
    let symbols = vec![
        ("ρ", "rho", "Greek letter rho"),
        ("φ", "phi", "Greek letter phi"),
        ("τ", "tau", "Greek letter tau"),
        ("ν", "nu", "Greek letter nu"),
        ("⊢", "|-", "Turnstile (proves)"),
        ("⇨", "=>", "Rightwards wave arrow"),
        ("⟿", "~>", "Rightwards wave"),
        ("▷", ">", "Right triangle"),
        ("≔", ":=", "Definition equals"),
        ("⊗", "*", "Tensor product"),
        ("≡", "===", "Equivalence"),
        ("∙", "·", "Bullet operator"),
        ("⟦", "[[", "Double bracket left"),
        ("⟧", "]]", "Double bracket right"),
        (":: ∎", ":: QED", "QED block terminator"),
    ];

    println!("Symbol Comparison:");
    println!("{:<10} {:<10} {:<8} {:<30}", "Unicode", "ASCII", "Ratio", "Description");
    println!("{}", "-".repeat(70));

    for (unicode, ascii, desc) in symbols {
        let unicode_chars = unicode.chars().count();
        let ascii_chars = ascii.chars().count();
        let ratio = unicode_chars as f64 / ascii_chars as f64;
        
        println!(
            "{:<10} {:<10} {:<8.2} {:<30}",
            unicode, ascii, ratio, desc
        );
    }
    println!(":: ∎\n");

    // Example analysis
    let examples = vec![
        (
            "PHENO.CHAIN\nρ{Input} ≔ ingest.chat{{chat}}\nφ{Classify} ≔ map.to.allowed\nτ{Output} ≔ emit.single.label\nEND",
            "## PHENO.CHAIN\nrho_input = ingest.chat(chat)\nphi_classify = map.to.allowed\ntau_output = emit.single.label\n## END"
        ),
        (
            "(ρ ⊗ φ ⊗ τ) ⇨ PRISM",
            "(rho * phi * tau) => PRISM"
        ),
        (
            "⊢ ≔ bind.input\n⇨ ≔ direct.flow\n⟿ ≔ carry.motion\n▷ ≔ project.output",
            "turnstile := bind.input\narrow := direct.flow\nwave := carry.motion\ntriangle := project.output"
        ),
    ];

    println!("Example Comparisons:\n");
    for (i, (unicode_ver, ascii_ver)) in examples.iter().enumerate() {
        let unicode_len = unicode_ver.chars().count();
        let ascii_len = ascii_ver.chars().count();
        let ratio = unicode_len as f64 / ascii_len as f64;
        
        println!("Example {}:", i + 1);
        println!("  Unicode version: {} chars", unicode_len);
        println!("  ASCII version:   {} chars", ascii_len);
        println!("  Ratio:           {:.2}x", ratio);
        println!();
    }
    println!(":: ∎\n");

    // Recommendations
    println!("Key Findings:");
    println!();
    println!("✅ Keep These:");
    println!("   :: ∎  - Strong semantic boundary");
    println!("   ≔     - Clear definition operator");
    println!("   ≡     - Equivalence (well-recognized)");
    println!("   ⊢     - Turnstile (type theory)");
    println!();
    println!("⚠️  Use Carefully:");
    println!("   ρ φ τ ν - Great in R/stats, avoid in general code");
    println!("   ⇨ ▷    - Need explicit definition");
    println!();
    println!("❌ Consider Replacing:");
    println!("   ⟿     - Low LLM recognition");
    println!("   ⟦ ⟧   - Use [[ ]] instead");
    println!();
    println!(":: ∎");
    
    println!("\n///▙▖▙▖▞▞▙▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂▂");
}
