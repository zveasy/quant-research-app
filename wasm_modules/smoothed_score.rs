use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn smooth(x: f64, alpha: f64) -> f64 {
    static mut LAST: f64 = 0.0;
    unsafe {
        let val = alpha * x + (1.0 - alpha) * LAST;
        LAST = val;
        val
    }
}
