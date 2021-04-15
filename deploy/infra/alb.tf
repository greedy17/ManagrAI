resource "aws_alb" "main" {
  name            = "managr-load-balancer"
  subnets         = aws_subnet.public.*.id
  security_groups = [aws_security_group.lb.id]

  tags = {
    "app" = "managr"
  }
}

resource "random_string" "alb_prefix" {
  length  = 4
  upper   = false
  special = false

}

resource "aws_alb_target_group" "app" {
  name        = "managr-target-group-${random_string.alb_prefix.result}"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"

  health_check {
    healthy_threshold   = "3"
    interval            = "30"
    protocol            = "HTTP"
    matcher             = "200"
    timeout             = "3"
    path                = var.health_check_path
    unhealthy_threshold = "2"
  }

  deregistration_delay = 0

  tags = {
    "app" = "managr"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_alb_listener" "front_end" {
  load_balancer_arn = aws_alb.main.id
  port              = var.app_port
  protocol          = "HTTP"

  default_action {
    target_group_arn = aws_alb_target_group.app.id
    type             = "forward"
  }
}

resource "aws_alb_listener" "front_end_https" {
  load_balancer_arn = aws_alb.main.id
  port              = var.app_port_https
  protocol          = "HTTPS"
  certificate_arn   = aws_acm_certificate.managr.arn

  default_action {
    target_group_arn = aws_alb_target_group.app.id
    type             = "forward"
  }
}

resource "tls_private_key" "managr" {
  algorithm = "RSA"
}

resource "tls_self_signed_cert" "managr" {
  key_algorithm   = "RSA"
  private_key_pem = tls_private_key.managr.private_key_pem

  subject {
    common_name  = aws_alb.main.dns_name
    organization = "WeissTech"
  }

  validity_period_hours = 12

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

resource "aws_acm_certificate" "managr" {
  private_key      = tls_private_key.managr.private_key_pem
  certificate_body = tls_self_signed_cert.managr.cert_pem
}
