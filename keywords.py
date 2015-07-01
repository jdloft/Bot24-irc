def check( msg, trusted ):
    response = ""
    if not msg[6] == False:
        if msg[6] == "help":
            if trusted:
                response = """Bot24 - Help

                    Commands:
                        help - this help text

                    Trusted user commands:
                        stop - shutdown bot
                        restart - restart bot"""
            else:
                response = """Bot24 - Help
                    Commands:
                        help - this help text"""
        elif ( msg[6] == "hi" or msg[6] == "hello" ):
            response = "Hello!"
    else:
        if msg[4].find( "bot24" ) != -1:
            response = "Hello!"
    return response
