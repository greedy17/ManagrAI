<template>
  <div class="reminder" @click="$emit('item-click')">
    <div class="item-list__item item-list__item--hover-effect">
      <div class="item-list__row">
        <div class="item-list__row-item--half">
          <img alt="icon" :src="require(`@/assets/images/pencil.svg`)" class="icon" />
        </div>
        <div class="item-list__row-item--double">
          <strong>{{ log.meta.title }}</strong>
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
        <p>{{ log.meta.content }}</p>
        <p>Reminder Set For {{ moment(log.meta.datetimeFor).format('MMM DD yy') }}</p>
        <p v-if="log.meta.linkedContacts && log.meta.linkedContacts.length">
          Contacts:
          {{ log.meta.linkedContactsRef.map(c => c.full_name).join(', ') }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import LogItemArrowIcon from './__LogItemArrowIcon'
import moment from 'moment'
export default {
  name: 'ReminderLogItem',
  components: { LogItemArrowIcon },
  props: {
    log: {
      type: Object,
      required: true,
    },

    collapsed: Boolean,
  },
  data() {
    return {
      moment: moment,
    }
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/containers';

.date-text {
  color: $mid-gray;
}
</style>
