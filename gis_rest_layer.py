if __name__ == '__main__':
    from restlayer import create_app
    app = create_app()
    app.run(host='0.0.0.0', port=app.config.get('APP_PORT', '5000'), processes=1 )
