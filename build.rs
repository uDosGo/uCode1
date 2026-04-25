fn main() {
    println!("cargo:rustc-check-cfg=cfg(user_mode)");
}