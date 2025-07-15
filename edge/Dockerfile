FROM rust:1.78-slim as builder
WORKDIR /app
COPY gateway.rs ./src/main.rs
RUN rustup target add x86_64-unknown-linux-musl && \
    cargo new --bin gateway && mv src/main.rs gateway/src/main.rs && \
    cd gateway && cargo build --release --target x86_64-unknown-linux-musl

FROM scratch
COPY --from=builder /app/gateway/target/x86_64-unknown-linux-musl/release/gateway /gateway
ENTRYPOINT ["/gateway"]
