#include <stdio.h>
#include <unistd.h>

int main(void) {
    pid_t pid = getpid();
    printf("agent v0, pid=%d\n", (int)pid);
    printf("Press Enter to exit\n");
    getchar();
    return 0;
}
