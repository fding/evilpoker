#include <stdio.h>
#include <stdarg.h>

#include "game.h"
#include "net.h"

class PokerProtocol {
public:
    PokerProtocol(const char* host, int port) {
        port = port;
        connected = false;
    }

    bool send_str(const char* fmt, ...) {
        va_list vl;
        va_start(vl, fmt);
        vfprintf(toServer, fmt, vl);
        va_end(vl);

        fflush(toServer);
    }

    int read_state(Game* game, State* state) {
        while (fgets(line, 4096, fromServer)) {
            // ignore comments
            if (line[0] == '#' || line[0] == ';')
                continue;

            len = readMatchState(line, game, &state);
            return len;
        }
    }

    int do_action(Game* game, State* state, Action* action) {
        line[len++] = ':';
        int r = printAction(game, action, 4096 - len - 2, &line[len]);
        if (r < 0) {
            return r;
        }
        len += r;
        line[len++] = '\r';
        line[len++] = '\n';
        if (fwrite(line, 1, len, toServer) != len) {
            return -1;
        }
        fflush(toServer);
        return 0;
    }

    bool connect() {
        sock = connectTo(host, port);
        if (sock < 0) {
            return false;
        }
        connected = true;
        toServer = fdopen(sock, "w");
        fromServer = fdopen(sock, "r");
        if (!toServer || !fromServer) {
            return false;
        }
        send_str("VERSION:2.0.0\n");
    }

private:
    int sock;
    int port;
    char line[4096];
    int len;
    FILE *toServer, *fromServer;
    bool connected;
};
