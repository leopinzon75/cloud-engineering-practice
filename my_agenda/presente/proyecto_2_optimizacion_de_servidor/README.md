# ⚡ OpenResty API Gateway & High-Speed Rate Limiter

Welcome! This project is a lightweight, high-performance API Gateway designed to manage web traffic, protect backend systems from overload, and ensure smooth server operation during high-traffic bursts.

---

## 💡 What Does This Project Do?

Imagine a popular store on opening day—if too many people try to enter through the door at the exact same moment, the store gets crowded and service slows down. 

This API Gateway acts like a smart bouncer at the door:
- **Smooth Traffic Flow:** It allows legitimate user requests to pass through instantly.
- **Fair Usage Limits:** It tracks incoming requests by client IP address using the **Token Bucket** strategy.
- **Overload Protection:** If a user sends too many requests too quickly, the system gently holds them back with a friendly `429 Too Many Requests` message until their quota resets.

---

## 🛠️ Built With

- **OpenResty / Nginx:** Ultra-fast web server foundation.
- **Lua:** Embedded scripting language for real-time traffic decisions with near-zero delay.
- **Docker:** Lightweight container setup for easy deployment anywhere.
- **GitHub Actions:** Automated building and delivery directly to Docker Hub.

---

## 🚀 How to Run Locally with Docker

You can launch and test the API Gateway locally using Docker:

```bash
# 1. Build the Docker image locally
docker build -t openresty-rate-limiter .

# 2. Run the container on port 8080
docker run -d --name rate_limiter_app -p 8080:8080 openresty-rate-limiter


Quick Test: Traffic Burst Simulation
To test the Token Bucket rate limiter in real time, run this loop in your terminal to send a rapid burst of 12 requests:

for i in {1..12}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8080/api; done

Expected Output:
Plaintext


200
200
200
200
200
200
200
200
200
200
429
429

Output Explanation
Requests 1 to 10 (200 OK): The bucket starts with a capacity of 10 tokens. The first 10 requests consume one token each and successfully reach the backend API.

Requests 11 & 12 (429 Too Many Requests): Once all 10 tokens are exhausted during a burst, the Lua script instantly intercepts subsequent requests at the Nginx layer and rejects them with a 429 status code, shielding downstream servers.



Container Cleanup Command
After completing your tests, clean up your Docker environment with the following command:

Bash


docker stop rate_limiter_app && docker rm rate_limiter_app

Plaintext


rate_limiter_app
rate_limiter_app

Output Explanation
First line (rate_limiter_app): Confirms that docker stop successfully halted the running OpenResty process.

Second line (rate_limiter_app): Confirms that docker rm successfully removed the stopped container instance from your machine.


Automated CI/CD Pipeline
Every update pushed to this repository automatically triggers a GitHub Actions workflow that builds the Docker image and publishes it to Docker Hub, keeping the deployment always up-to-date.
