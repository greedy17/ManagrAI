<template>
  <div class="email-action">
    <div class="item-list__item item-list__item--hover-effect">
      <div class="item-list__row" @click="$emit('item-click')">
        <div class="item-list__row-item--half">
          <div class="icon-type">
            <img alt="icon" :src="require(`@/assets/images/email.svg`)" class="icon" />
            <small class="muted">
              <svg class="icon-viewed">
                <use xlink:href="@/assets/images/eye.svg#eye" />
              </svg>

              {{ log.meta.openedCount ? log.meta.openedCount : 0 }}
            </small>
          </div>
        </div>
        <div class="item-list__row-item--double">
          <strong
            >{{
              log.activity == 'LeadEmail.RECEIVED'
                ? `Email Received  From ${getLinkedContacts}`
                : `Email Sent To ${getLinkedContacts}`
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
        <p v-if="log.activity == 'LeadEmail.RECEIVED'">
          {{ log.actionTakenByRef.fullName }} Received an Email From {{ getLinkedContacts }}
        </p>
        <p v-if="log.activity == 'LeadEmail.SENT'">
          {{ log.actionTakenByRef.fullName }} sent an email to {{ getLinkedContacts }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import LogItemArrowIcon from './__LogItemArrowIcon'

export default {
  name: 'EmailLogItem',
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

.date-text {
  color: $mid-gray;
}
.icon-viewed {
  width: 10px;
  height: 10px;
}
.icon-type {
  display: flex;
  justify-content: flex-start;
  > img {
    flex: 1 0 auto;
    margin-left: -3.5rem;
  }
}
</style>
