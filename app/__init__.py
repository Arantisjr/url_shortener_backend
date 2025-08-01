from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
import logging
from sqlalchemy import inspect, text as db_text

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    
    # 1. Load configuration
    app.config.from_object(config_class)
    
    # Verify configuration
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise RuntimeError("Database URI not configured!")

    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Enable SQLAlchemy logging
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # 2. Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Import models after db initialization
    from app.models import User, ShortURL

    with app.app_context():
        # 3. Verify and create tables
        inspector = inspect(db.engine)
        required_tables = {'user', 'short_url'}
        existing_tables = set(inspector.get_table_names())
        
        if not required_tables.issubset(existing_tables):
            logger.info("🛠 Creating database tables...")
            try:
                db.create_all()
                
                # Verify creation
                created_tables = set(inspect(db.engine).get_table_names())
                missing_tables = required_tables - created_tables
                if missing_tables:
                    logger.error(f"❌ Missing tables: {missing_tables}")
                    # Try creating tables individually
                    if 'user' in missing_tables:
                        User.__table__.create(db.engine)
                    if 'short_url' in missing_tables:
                        ShortURL.__table__.create(db.engine)
                    
                    # Re-check
                    created_tables = set(inspect(db.engine).get_table_names())
                    missing_tables = required_tables - created_tables
                    if missing_tables:
                        raise RuntimeError(f"Failed to create tables: {missing_tables}")
                
                logger.info("✅ Tables created successfully")
            except Exception as e:
                logger.error(f"❌ Table creation failed: {str(e)}")
                raise RuntimeError(f"Database setup failed: {str(e)}") from e
        else:
            logger.info("✅ Database tables already exist")

        # 4. Test connection
        try:
            with db.engine.connect() as conn:
                result = conn.execute(db_text("SELECT 1"))
                if result.scalar() == 1:
                    logger.info("✅ Database connection successful!")
                else:
                    raise RuntimeError("Database test query failed")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {str(e)}")
            raise

    # 5. Initialize OAuth
    from app.oauth import init_oauth
    init_oauth(app)
    
    # 6. Register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp, url_prefix='/api')
    
    from app.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # 7. Error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    # 8. Production settings
    if not app.debug:
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'pool_timeout': 30,
            'max_overflow': 20,
            'pool_size': 10
        }

    return app