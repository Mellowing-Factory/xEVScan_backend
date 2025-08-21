from flask import Flask
from flask_cors import CORS
from flask_restx import Api
from config import Config
from extensions import db, bcrypt, jwt, mail, limiter
from swagger_models import create_swagger_models
from flask_migrate import Migrate
from middleware import setup_rate_limiting, setup_logging


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    CORS(app)

    # After creating app and db instances
    migrate = Migrate(app, db)

    # After creating app
    limiter.init_app(app)  # Initialize limiter
    
    # Initialize Swagger API
    api = Api(
        app,
        version='1.0',
        title='EV Scan API',
        description='Electric Vehicle Diagnostic Scan Data Management API',
        doc='/docs/',
        prefix='/api',
        authorizations={
            'Bearer': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'JWT Authorization header using the Bearer scheme. Example: "Authorization: Bearer {token}"'
            }
        },
        security='Bearer'
    )
    
    # Create Swagger models
    models = create_swagger_models(api)
    
    # Import and register namespaces
    from api.auth_swagger import auth_ns
    from api.user_swagger import user_ns
    from api.external_swagger import external_ns
    from api.tablet_swagger import tablet_ns
    from api.data_spec_swagger import data_spec_ns
    
    # Pass models to namespaces
    auth_ns.models = models
    user_ns.models = models
    external_ns.models = models
    tablet_ns.models = models
    data_spec_ns.models = models
    
    # Register namespaces
    api.add_namespace(auth_ns, path='/auth')
    api.add_namespace(user_ns, path='/user')
    api.add_namespace(external_ns, path='/external')
    api.add_namespace(tablet_ns, path='/tablet')
    api.add_namespace(data_spec_ns, path='/')
    
    # Health check route (outside of API documentation)
    @app.route('/')
    def health_check():
        from datetime import datetime
        from flask import jsonify
        return jsonify({
            'status': 'healthy',
            'service': 'EV Scan API',
            'timestamp': datetime.utcnow().isoformat(),
            'documentation': '/docs'
        })
    
    return app

if __name__ == '__main__':
    import os
    app = create_app()
    
    with app.app_context():
        db.create_all()
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)