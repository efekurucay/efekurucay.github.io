#include "contiki.h"
#include "net/rime/rime.h"
#include "net/packetbuf.h"
#include <stdio.h>
#include <stdint.h>

PROCESS(sender_process, "Radio lab sender");
AUTOSTART_PROCESSES(&sender_process);

static struct broadcast_conn broadcast;

static void
broadcast_recv(struct broadcast_conn *c, const linkaddr_t *from)
{
  /* Sender does not process received packets. */
}

static const struct broadcast_callbacks broadcast_call = {
  broadcast_recv
};

PROCESS_THREAD(sender_process, ev, data)
{
  static struct etimer timer;
  static uint16_t seq = 0;

  PROCESS_EXITHANDLER(broadcast_close(&broadcast);)
  PROCESS_BEGIN();

  broadcast_open(&broadcast, 129, &broadcast_call);
  etimer_set(&timer, CLOCK_SECOND);

  while(1) {
    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));
    seq++;
    packetbuf_copyfrom(&seq, sizeof(seq));
    broadcast_send(&broadcast);
    printf("TX seq=%u\n", seq);
    etimer_reset(&timer);
  }

  PROCESS_END();
}
