import os
from src import create_app

# 1. Generate the app using the factory
app = create_app()

if __name__ == '__main__':
    # 2. Extract the server variables from the configuration
    server_host = app.config.get('HOST', '127.0.0.1')
    server_port = app.config.get('PORT', 5000)

    # 3. Run the development server
    app.run(host=server_host, port=server_port)
