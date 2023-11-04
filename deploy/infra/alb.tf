resource "aws_alb" "main" {
  name            = "managr-load-balancer"
  subnets         = aws_subnet.public.*.id
  security_groups = [aws_security_group.lb.id]
  tags = {
    "app" = "managr"
  }
  enable_http2 = true
  idle_timeout = 600
}

resource "random_string" "alb_prefix" {
  for_each = { for e in var.environments : e.name => e }
  length   = 4
  upper    = false
  special  = false
}

resource "aws_alb_target_group" "app" {
  for_each    = { for e in var.environments : e.name => e }
  name        = "managr-target-group-${lower(each.value["name"])}-${random_string.alb_prefix[each.key].result}"
  port        = 80
  protocol    = "HTTP"
  vpc_id      = aws_vpc.main.id
  target_type = "ip"
  health_check {
    healthy_threshold   = "3"
    interval            = "60"
    protocol            = "HTTP"
    matcher             = "301"
    timeout             = "30"
    path                = var.health_check_path
    unhealthy_threshold = "2"
  }


  deregistration_delay = 30

  tags = {
    "app" = "managr"
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_alb_listener" "front_end" {
  load_balancer_arn = aws_alb.main.id
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

resource "aws_alb_listener" "front_end_https" {
  load_balancer_arn = aws_alb.main.id
  port              = 443
  protocol          = "HTTPS"
  certificate_arn   = "arn:aws:acm:us-east-1:986523545926:certificate/07f76f44-4c27-4112-a768-d7ea0afd9e34"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"

  default_action {
    target_group_arn = aws_alb_target_group.app["prod"].id
    type             = "forward"
  }
}

resource "tls_private_key" "managr" {
  algorithm = "RSA"
  rsa_bits  = 4096  # Use a 4096-bit RSA key for stronger encryption
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

resource "aws_lb_listener_rule" "rule_https" {
  for_each     = { for e in var.environments : e.name => e }
  listener_arn = aws_alb_listener.front_end_https.arn
  priority     = 10 + index(tolist(var.environments), each.value)

  action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.app[each.key].id
  }

  condition {
    host_header {
      values = [each.value.name == "prod" ? "app.${var.managr_domain}" : "${each.value.name}.${var.managr_domain}"]
    }
  }
}

resource "aws_lb_listener_rule" "rule_https_default" {
  listener_arn = aws_alb_listener.front_end_https.arn
  priority     = 200

  action {
    type             = "forward"
    target_group_arn = aws_alb_target_group.app["prod"].id
  }

  condition {
    host_header {
      values = [var.managr_domain]
    }
  }
}

resource "aws_lb_listener_rule" "rule_http_redirect" {
  listener_arn = aws_alb_listener.front_end.arn
  priority        = 100

  action {
    type          = "redirect"
    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }

  condition {
    http_header {
      http_header_name  = "X-Forwarded-Proto"
      values            = ["http"]
    }
  }
}