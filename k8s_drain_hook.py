from __future__ import annotations

import os
from typing import Any

from flask import Flask, request
from kubernetes import client, config

app = Flask(__name__)


def cordon_and_drain(node_name: str) -> None:
    v1 = client.CoreV1Api()
    # cordon
    v1.patch_node(node_name, {"spec": {"unschedulable": True}})
    # drain respecting PDBs via eviction API
    pods = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node_name}").items
    for p in pods:
        if p.metadata.owner_references and any(o.kind == "DaemonSet" for o in p.metadata.owner_references):
            continue
        body = client.V1Eviction(metadata=client.V1ObjectMeta(name=p.metadata.name, namespace=p.metadata.namespace))
        try:
            v1.create_namespaced_pod_eviction(p.metadata.name, p.metadata.namespace, body)
        except client.exceptions.ApiException:
            pass


@app.route("/hook", methods=["POST"])
def hook() -> tuple[str, int]:
    data: dict[str, Any] = request.get_json(force=True)
    for alert in data.get("alerts", []):
        node = alert.get("labels", {}).get("node")
        if node:
            cordon_and_drain(node)
    return "ok", 200


def main() -> None:
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        config.load_incluster_config()
    else:
        config.load_kube_config()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))


if __name__ == "__main__":
    main()
