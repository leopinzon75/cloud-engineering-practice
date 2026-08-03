# ==========================================
# CONFIGURACIÓN TOTALMENTE BLINDADA PARA LOCALSTACK
# ==========================================
provider "aws" {
  region                      = "us-east-1"
  access_key                  = "mock_access_key"
  secret_key                  = "mock_secret_key"
  
  # Desactivación absoluta de validaciones de AWS Real
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  skip_region_validation      = true
  
  # Forzar estilo de rutas e ignorar firmas SSL locales
  s3_use_path_style           = true

  endpoints {
    s3       = "http://127.0.0.1:4566"
    dynamodb = "http://127.0.0.1:4566"
  }
}

# ==========================================
# ALMACENAMIENTO PERSISTENTE (S3)
# ==========================================
resource "aws_s3_bucket" "storage_bucket" {
  bucket = "fase5-storage-bucket"
}

# ==========================================
# CONTROL DE CONCURRENCIA Y BLOQUEOS (DYNAMODB)
# ==========================================
resource "aws_dynamodb_table" "execution_locks" {
  name         = "fase5-execution-locks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Environment = "Local-Dev"
    Phase       = "Phase-5"
  }
}
