// dealer.nqc -- deals cards!

// motors
#define DEALER OUT_A
#define FILTER OUT_B
#define ROTATOR OUT_C

// sensors
#define CCOUNT SENSOR_1 // card count
#define RCOUNT SENSOR_3 // rotation count (6 positions)

// constants
#define PLAYERS 4
#define CARDS 6
#define DEALINGMODE 0 // 0 for dealing in sequence, 1 for dealing all at once
#define FREQ 440

int pos;
int position = 1;
int cards = 0;
int quit = 0;

task main() {
    // sensor/motor initialization
    SetSensor(CCOUNT, SENSOR_TOUCH);
    SetSensorMode(RCOUNT, SENSOR_TOUCH);
    SetPower(FILTER, OUT_HALF);

    // task initialization
    start update_position;
    start update_cards;
    start rotate;
    start dealt;

    // exit!
    if (quit) {
        StopAllTasks();
        return;
    }
}

task dealt() {
    // are all the cards dealt?
    while (true) {
        if (cards == PLAYERS*CARDS)
            quit = 1;
        else
            quit = 0;
    }
}
            
void deal(const int &n) {
    int i;
    for (i = 1; i <= n; i++) {
        until (CCOUNT == 1) {
            On(DEALER);
            On(FILTER);
        }
        Off(FILTER);
        Wait(50);
        Off(DEALER);
    }
}

task rotate() {
    while (true) {
        int cpos = pos;
        while (cpos + 1 != pos) {
            On(ROTATOR);
        }
        if (cpos + 1 == pos && position <= PLAYERS) {
            Off(ROTATOR);
            deal(1);
            On(ROTATOR);
            Wait(50);
        }
    }
}        

task update_position() {
    while (true) {
        if (RCOUNT == 0) {
            Wait(30);
            if (RCOUNT == 0) {
                pos++;
                if (position + 1 <= 6)
                    position++;
                else
                    position = 1;
            }
        }
    }
}