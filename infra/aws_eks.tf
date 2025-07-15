resource "aws_eks_cluster" "this" {
  name     = var.cluster_name
  role_arn = var.role_arn

  vpc_config {
    subnet_ids = var.subnet_ids
  }
}

resource "aws_eks_node_group" "spot" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "spot"
  node_role_arn   = var.node_role_arn
  subnet_ids      = var.subnet_ids
  capacity_type   = "SPOT"
  scaling_config {
    desired_size = 1
    max_size     = 2
    min_size     = 1
  }
  tags = {
    env = "research"
  }
}

resource "aws_eks_node_group" "on_demand" {
  cluster_name    = aws_eks_cluster.this.name
  node_group_name = "on-demand"
  node_role_arn   = var.node_role_arn
  subnet_ids      = var.subnet_ids
  capacity_type   = "ON_DEMAND"
  scaling_config {
    desired_size = 1
    max_size     = 2
    min_size     = 1
  }
  tags = {
    env = "research"
  }
}

output "kubeconfig" {
  value = aws_eks_cluster.this.kubeconfig[0]
}

output "cost_tags" {
  value = {
    spot      = aws_eks_node_group.spot.tags
    on_demand = aws_eks_node_group.on_demand.tags
  }
}
