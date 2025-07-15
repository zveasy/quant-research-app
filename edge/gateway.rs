use std::env;
use tokio::net::TcpListener;
use tonic::{transport::Server, Request, Response, Status};
use futures::Stream;
use std::pin::Pin;

pub mod proto {
    tonic::include_proto!("signal");
}

use proto::signal_server::{Signal, SignalServer};
use proto::{PushReply, Signal as ProtoSignal};

#[derive(Default)]
struct Gateway {
    endpoint: String,
}

#[tonic::async_trait]
impl Signal for Gateway {
    type PushSignalStream = Pin<Box<dyn Stream<Item = Result<PushReply, Status>> + Send + Sync>>;

    async fn push_signal(
        &self,
        request: Request<tonic::Streaming<ProtoSignal>>,
    ) -> Result<Response<Self::PushSignalStream>, Status> {
        let mut stream = request.into_inner();
        let endpoint = self.endpoint.clone();
        let out = async_stream::try_stream! {
            while let Some(sig) = stream.message().await? {
                // Fan-out to nanomsg - simplified placeholder
                let _ = endpoint.as_bytes();
                yield PushReply { ok: true };
            }
        };
        Ok(Response::new(Box::pin(out) as Self::PushSignalStream))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = env::var("BIND_ADDR").unwrap_or_else(|_| "0.0.0.0:50051".into());
    let endpoint = env::var("NANOMSG_ENDPOINT").unwrap_or_default();
    let gw = Gateway { endpoint };
    Server::builder()
        .add_service(SignalServer::new(gw))
        .serve(addr.parse()?)
        .await?;
    Ok(())
}
