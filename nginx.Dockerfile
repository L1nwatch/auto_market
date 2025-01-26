# Use the official Nginx base image
FROM nginx:latest

# Set the working directory inside the container
WORKDIR /etc/nginx

# Copy your custom nginx.conf file into the container
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80 to allow external traffic
EXPOSE 80

# Start Nginx in the foreground (default CMD for Nginx)
CMD ["nginx", "-g", "daemon off;"]
