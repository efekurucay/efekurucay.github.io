#include "contiki.h"
#include "net/rime/rime.h"
#include "net/packetbuf.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>

PROCESS(receiver_process, "Radio lab receiver");
AUTOSTART_PROCESSES(&receiver_process);

static struct broadcast_conn broadcast;

static void
broadcast_recv(struct broadcast_conn *c, const linkaddr_t *from)
{
  uint16_t seq;
  int8_t rssi_raw;
  int16_t rssi_dbm;
  uint16_t lqi;

  if(packetbuf_datalen() >= sizeof(seq)) {
    memcpy(&seq, packetbuf_dataptr(), sizeof(seq));
    rssi_raw = (int8_t)packetbuf_attr(PACKETBUF_ATTR_RSSI);
    /* CC2420 RSSI uses an approximately -45 dB offset. */
    rssi_dbm = ((int16_t)rssi_raw) - 45;
    lqi = packetbuf_attr(PACKETBUF_ATTR_LINK_QUALITY);
    printf("RX seq=%u RSSI=%d dBm LQI=%u\n", seq, rssi_dbm, lqi);
  }
}

static const struct broadcast_callbacks broadcast_call = {
  broadcast_recv
};

PROCESS_THREAD(receiver_process, ev, data)
{
  PROCESS_EXITHANDLER(broadcast_close(&broadcast);)
  PROCESS_BEGIN();

  broadcast_open(&broadcast, 129, &broadcast_call);

  while(1) {
    PROCESS_YIELD();
  }

  PROCESS_END();
}
