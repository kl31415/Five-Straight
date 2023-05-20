#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>
#include <math.h>

// Constants
int NUM_PEOPLE = 4;
int PLAYERS_PER_TEAM = 2;

// Global variables
int all_cards[100];
int start_position = 16;
int p1_cards[4];
int p2_cards[4];
int p3_cards[4];
int p4_cards[4];
int num_cards_p1 = 4;
int num_cards_p2 = 4;
int num_cards_p3 = 4;
int num_cards_p4 = 4;

// Declaration of function to be used:
int gettimeofday(struct timeval *tp, struct timezone *tz); 

// Algorithm to shuffle cards, cite stackoverflow question 6127503, shuffle array in c
void shuffle(int* array, int n) {    
    struct timeval tv;
    gettimeofday(&tv, NULL);
    int usec = tv.tv_usec;
    srand48(usec);

    if (n > 1) {
        size_t i;
        for (i = n - 1; i > 0; i--) {
            size_t j = (unsigned int) (drand48()*(i+1));
            int t = array[j];
            array[j] = array[i];
            array[i] = t;
        }
    }
}

// Shuffle cards
void full_shuffle() {
    for (int i = 0; i < 100; i++) {
        all_cards[i] = i;
    }
    for (int i = 0; i < 5; i++) {
        shuffle(all_cards, 100);
    }
}

// Deal starting cards to everyone
void deal_cards() {
    for (int i = 0; i < 4; i++) {
        p1_cards[i] = all_cards[NUM_PEOPLE*i];
        p2_cards[i] = all_cards[NUM_PEOPLE*i + 1];
        p3_cards[i] = all_cards[NUM_PEOPLE*i + 2];
        p4_cards[i] = all_cards[NUM_PEOPLE*i + 3];
    }
}

// Board setup
int board[10][10] = {
    {73, 72, 71, 70, 69, 68, 67, 66, 65, 0},
    {74, 57, 58, 59, 60, 61, 62, 63, 64, 99},
    {75, 56, 21, 20, 19, 18, 17, 36, 37, 98},
    {76, 55, 22, 13, 14, 15, 16, 35, 38, 97},
    {77, 54, 23, 12, 1, 4, 5, 34, 39, 96},
    {78, 53, 24, 11, 2, 3, 6, 33, 40, 95},
    {79, 52, 25, 10, 9, 8, 7, 32, 41, 94},
    {80, 51, 26, 27, 28, 29, 30, 31, 42, 93},
    {81, 50, 49, 48, 47, 46, 45, 44, 43, 92},
    {82, 83, 84, 85, 86, 87, 88, 89, 90, 91}
};
void setup_board() {
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < 10; j++) {
            board[i][j] = board[i][j]<<3;
        }
    }
}

// Output colors
void red() {
    printf("\033[1;31m");
}
void green() {
    printf("\033[1;32m");
}
void yellow() {
    printf("\033[1;33m");
}
void blue() {
    printf("\033[1;34m");
}
void purple() {
    printf("\033[1;35m");
}
void cyan() {
    printf("\033[1;36m");
}
void white() {
    printf("\033[0;37m");
}
void reset() {
    printf("\033[0m");
}

// Printing out boxes
void print_box(i, j) {
    if (((board[i][j] & 7) == 1) || ((board[i][j] & 7) == 3)) {
        purple();
    } else if (((board[i][j] & 7) == 2) || ((board[i][j] & 7) == 4)) {
        cyan();
    }
    if (board[i][j]>>3 < 10) {
        printf("%d", 0);
    }
    printf("%d", board[i][j]>>3);
    reset();
    printf(" ");
}

// Board display
void display_board() {
    printf("\n");
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < 10; j++) {
            white();
            print_box(i, j);
        }
        printf("\n");
    }
    printf("\n");
    reset();
}

// Check if typed number is in hand
bool included(int cur, int* cards) {
    for (int i = 0; i < 4; i++) {
        if (cur == cards[i]) {
            return true;
        }
    }
    return false;
}

// Check if playing in this location is valid
bool valid_move(int loc, int board[10][10]) {
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < 10; j++) {
            if (loc == (board[i][j]>>3)) {
                if ((board[i][j] & 7) == 0) {
                    return true;
                } else {
                    return false;
                }
            }
        }
    }
    return false;
}

void move(int loc, int player_num, int board[10][10]) {
    for (int i = 0; i < 10; i++) {
        for (int j = 0; j < 10; j++) {
            if (loc == (board[i][j]>>3)) {
                board[i][j] += player_num;
            }
        }
    }
}

// Check rows for a win
bool check_h() {
    for (int i = 1; i <= 2; i++) {
        for (int j = 0; j < 10; j++) {
            for (int k = 0; k < 6; k++) {
                int count = 0;
                for (int m = 0; m < 5; m++) {
                    if (((board[j][k+m] & 7) == i) || ((board[j][k+m] & 7) == i+2)) {
                        count++;
                    } else {
                        count = 0;
                    }
                }
                if (count >= 5) {
                    return true;
                }
            }
        }
    }
    return false;
}

// Check columns for a win
bool check_v() {
    for (int i = 1; i <= 2; i++) {
        for (int j = 0; j < 10; j++) {
            for (int k = 0; k < 6; k++) {
                int count = 0;
                for (int m = 0; m < 5; m++) {
                    if (((board[k+m][j] & 7) == i) || ((board[k+m][j] & 7) == i+2)) {
                        count++;
                    } else {
                        count = 0;
                    }
                }
                if (count >= 5) {
                    return true;
                }
            }
        }
    }
    return false;
}

// Check diagonals for a win
bool check_d() {
    for (int i = 1; i <= 2; i++) {
        // Top left to bottom right
        for (int j = 0; j < 6; j++) {
            for (int k = 0; k < 6; k++) {
                int count = 0;
                for (int m = 0; m < 5; m++) {
                    if (((board[j+m][k+m] & 7) == i) || ((board[j+m][k+m] & 7) == i+2)) {
                        count++;
                    } else {
                        count = 0;
                    }
                }
                if (count >= 5) {
                    return true;
                }
            }
        }
        // Top right to bottom left
        for (int j = 0; j < 6; j++) {
            for (int k = 9; k > 3; k--) {
                int count = 0;
                for (int m = 0; m < 5; m++) {
                    if (((board[j+m][k-m] & 7) == i) || ((board[j+m][k-m] & 7) == i+2)) {
                        count++;
                    } else {
                        count = 0;
                    }
                }
                if (count >= 5) {
                    return true;
                }
            }
        }
    }
    return false;
}

// Check if anyone won, credit to connect 4 java win conditions check
bool check_win() {
    return check_h() || check_v() || check_d();
}

// Sequence of actions for a "play"
void play(int cur, int* cards, int player_num) {
    printf("\nNow choose where to play it: ");
    int loc = -1;
    scanf("%d", &loc);
    while (!valid_move(loc, board) || (loc < cur)) {
        if (!valid_move(loc, board)) {
            printf("\nThat's already occupied! Please try again: ");
        } else {
            printf("\nThat's too small! Please try again: ");
        }
        scanf("%d", &loc);
    }
    move(loc, player_num, board);
    for (int i = 0; i < 4; i++) {
        if (cur == cards[i]) {
            cards[i] = -1;
        }
    }
    printf("\nCard played successfully. Moving on...\n\n");
}

// Sequence of actions for a "draw"
void draw(int* cards) {
    printf("\nDrawing card... Your new card is: ");
    int new = all_cards[start_position];
    start_position++;
    printf("%d", new);
    for (int i = 0; i < 4; i++) {
        if (cards[i] == -1) {
            cards[i] = new;
            break;
        }
    }
    printf("\n\nCard drawn successfully. Moving on...\n\n");
}

// Helper function to compare card values
int comp(const void* first, const void* second) {
    int one = *((int*)first);
    int two = *((int*)second);
    if (one == two) {
        return 0;
    } else if (first < second) {
        return -1;
    }
    return 1;
}

// Main gameplay section
int main() {
    full_shuffle();
    deal_cards();
    setup_board();
    while (true) {
        display_board();
        purple();
        printf("\nPlayer 1's turn. ");
        reset();
        printf("Here are your cards:\n\n");
        qsort(&p1_cards, 4, sizeof(int), comp);
        for (int i = 0; i < 4; i++) {
            if (p1_cards[i] != -1) {
                printf("%d", p1_cards[i]);
                printf(" ");
            }
        }
        printf("\n");
        if (num_cards_p1 == 4) {
            printf("\nPick a card to play: ");
            int cur = -1;
            scanf("%d", &cur);
            while (!included(cur, p1_cards)) {
                printf("\nYou don't currently have that card! Please try again: ");
                scanf("%d", &cur);
            }
            play(cur, p1_cards, 1);
            num_cards_p1--;
        } else if (num_cards_p1 == 0) {
            draw(p1_cards);
            num_cards_p1++;
        } else {
            printf("\nYou can either play (type in card value) or draw (type in -1): ");
            int option = -1;
            scanf("%d", &option);
            while (!included(option, p1_cards)) {
                printf("\nYou don't currently have that card! Please try again: ");
                scanf("%d", &option);
            }
            if (option == -1) {
                draw(p1_cards);
                num_cards_p1++;
            } else {
                play(option, p1_cards, 1);
                num_cards_p1--;
            }
        }
        if (check_win()) {
            display_board();
            yellow();
            printf("\nCONGRATULATIONS! PURPLE WINS!\n\n");
            reset();
            break;
        }
        display_board();
        cyan();
        printf("\nPlayer 2's turn. ");
        reset();
        printf("Here are your cards:\n\n");
        qsort(&p2_cards, 4, sizeof(int), comp);
        for (int i = 0; i < 4; i++) {
            if (p2_cards[i] != -1) {
                printf("%d", p2_cards[i]);
                printf(" ");
            }
        }
        printf("\n");
        if (num_cards_p2 == 4) {
            printf("\nPick a card to play: ");
            int cur = -1;
            scanf("%d", &cur);
            while (!included(cur, p2_cards)) {
                printf("\nYou don't currently have that card! Please try again: ");
                scanf("%d", &cur);
            }
            play(cur, p2_cards, 2);
            num_cards_p2--;
        } else if (num_cards_p2 == 0) {
            draw(p2_cards);
            num_cards_p2++;
        } else {
            printf("\nYou can either play (type in card value) or draw (type in -1): ");
            int option = -1;
            scanf("%d", &option);
            while (!included(option, p2_cards)) {
                printf("\nYou don't currently have that card! Please try again: ");
                scanf("%d", &option);
            }
            if (option == -1) {
                draw(p2_cards);
                num_cards_p2++;
            } else {
                play(option, p2_cards, 2);
                num_cards_p2--;
            }
        }
        if (check_win()) {
            display_board();
            cyan();
            printf("\nCONGRATULATIONS! CYAN WINS!\n\n");
            reset();
            break;
        }
        display_board();
        purple();
        printf("\nPlayer 3's turn. ");
        reset();
        printf("Here are your cards:\n\n");
        qsort(&p3_cards, 4, sizeof(int), comp);
        for (int i = 0; i < 4; i++) {
            if (p3_cards[i] != -1) {
                printf("%d", p3_cards[i]);
                printf(" ");
            }
        }
        printf("\n");
        if (num_cards_p3 == 4) {
            printf("\nPick a card to play: ");
            int cur = -1;
            scanf("%d", &cur);
            while (!included(cur, p3_cards)) {
                printf("\nYou don't currently have that card! Please try again: ");
                scanf("%d", &cur);
            }
            play(cur, p3_cards, 3);
            num_cards_p3--;
        } else if (num_cards_p3 == 0) {
            draw(p3_cards);
            num_cards_p3++;
        } else {
            printf("\nYou can either play (type in card value) or draw (type in -1): ");
            int option = -1;
            scanf("%d", &option);
            while (!included(option, p3_cards)) {
                printf("\nYou don't currently have that card! Please try again: ");
                scanf("%d", &option);
            }
            if (option == -1) {
                draw(p3_cards);
                num_cards_p3++;
            } else {
                play(option, p3_cards, 3);
                num_cards_p3--;
            }
        }
        if (check_win()) {
            display_board();
            yellow();
            printf("\nCONGRATULATIONS! PURPLE WINS!\n\n");
            reset();
            break;
        }
        display_board();
        cyan();
        printf("\nPlayer 4's turn. ");
        reset();
        printf("Here are your cards:\n\n");
        qsort(&p4_cards, 4, sizeof(int), comp);
        for (int i = 0; i < 4; i++) {
            if (p4_cards[i] != -1) {
                printf("%d", p4_cards[i]);
                printf(" ");
            }
        }
        printf("\n");
        if (num_cards_p4 == 4) {
            printf("\nPick a card to play: ");
            int cur = -1;
            scanf("%d", &cur);
            while (!included(cur, p4_cards)) {
                printf("\nYou don't currently have that card! Please try again: ");
                scanf("%d", &cur);
            }
            play(cur, p4_cards, 4);
            num_cards_p4--;
        } else if (num_cards_p4 == 0) {
            draw(p4_cards);
            num_cards_p4++;
        } else {
            printf("\nYou can either play (type in card value) or draw (type in -1): ");
            int option = -1;
            scanf("%d", &option);
            while (!included(option, p4_cards)) {
                printf("\nYou don't currently have that card! Please try again: ");
                scanf("%d", &option);
            }
            if (option == -1) {
                draw(p4_cards);
                num_cards_p4++;
            } else {
                play(option, p4_cards, 4);
                num_cards_p4--;
            }
        }
        if (check_win()) {
            display_board();
            cyan();
            printf("\nCONGRATULATIONS! CYAN WINS!\n\n");
            reset();
            break;
        }
    }
    return 0;
}