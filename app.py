from map_app import create_app

if __name__ == "__main__":
    create_app().run(host='0.0.0.0', port=1337, debug=True)
    #create_app().run(host='0.0.0.0', port=1337, debug=False)