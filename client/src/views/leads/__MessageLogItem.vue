<template>
  <div class="email-action">
    <div class="item-list__item item-list__item--hover-effect">
      <div class="item-list__row" @click="$emit('item-click')">
        <div class="item-list__row-item--half">
          <div class="icon-type">
            <img alt="icon" :src="require(`@/assets/images/email.svg`)" class="icon" />
          </div>
        </div>
        <div class="item-list__row-item--double">
          <strong
            >{{
              log.activity == 'LeadMessage.RECEIVED'
                ? `Message Received  From ${getLinkedContacts}`
                : `Message Sent To ${getLinkedContacts}`
            }}
          </strong>
        </div>
        <div class="item-list__row-item--double">
          <span class="date-text">{{ log.actionTimestamp | dateShortWithTime }}</span>
        </div>

        <div class="item-list__row-item--half">
          <LogItemArrowIcon :down="collapsed" />
        </div>
      </div>
    </div>

    <div class="box--no-border" v-if="!collapsed">
      <div class="box__content">
        <div class="panel-content">
          <p v-if="log.activity == 'LeadMessage.RECEIVED'">
            {{ log.actionTakenByRef.fullName }} received Message From {{ getLinkedContacts }}
          </p>
          <p v-if="log.activity == 'LeadMessage.SENT'">
            {{ log.actionTakenByRef.fullName }} sent message to {{ getLinkedContacts }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LogItemArrowIcon from './__LogItemArrowIcon'

export default {
  name: 'MessageLogItem',
  components: { LogItemArrowIcon },
  props: {
    log: {
      type: Object,
      required: true,
    },
    collapsed: Boolean,
  },
  computed: {
    getLinkedContacts() {
      //most activity logs meta have linked_contacts but some older ones may not so check if they do first
      // will most likely fix this with a migration PB 07/16
      if (this.log.meta.linkedContacts) {
        return this.log.meta.linkedContacts.map(c => c.full_name).join(', ')
      }
      return []
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/containers';
@import '@/styles/variables';

.date-text {
  color: $mid-gray;
}
.icon-viewed {
  width: 25px;
  height: 25px;
  fill: rgba(47, 48, 53, 0.4);
}
.icon-type {
  display: flex;
  justify-content: flex-start;
}
.item-list__row-item--double {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}

.read-receipt {
  display: flex;
}
.muted {
  margin-right: 1rem;
}
</style>
