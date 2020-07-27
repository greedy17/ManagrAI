<template>
  <div class="call-note">
    <div class="item-list__item item-list__item--hover-effect">
      <div class="item-list__row" @click="$emit('item-click')">
        <div class="item-list__row-item--half">
          <img alt="icon" :src="require(`@/assets/images/claimed.svg`)" class="icon" />
        </div>
        <div class="item-list__row-item--double">
          <strong v-if="log.action === 'CLAIMED'">
            {{
              log.actionTakenByRef.fullName.trim()
                ? log.actionTakenByRef.fullName
                : log.actionTakenByRef.email
            }}
            claimed this lead.
          </strong>
          <strong v-if="log.action === 'RELEASED'">
            {{
              log.actionTakenByRef.fullName.trim()
                ? log.actionTakenByRef.fullName
                : log.actionTakenByRef.email
            }}
            released this lead.
          </strong>
          <strong v-if="log.action === 'UPDATED'">
            {{
              log.actionTakenByRef.fullName.trim()
                ? log.actionTakenByRef.fullName
                : log.actionTakenByRef.email
            }}
            made a change.
          </strong>
        </div>
        <div class="item-list__row-item--double">
          <span class="date-text">{{ log.actionTimestamp | dateShortWithTime }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * Displays Lead-related action log items.
 *
 * This item does not collapse/expand like others.
 */
export default {
  name: 'LeadLogItem',
  props: {
    log: {
      type: Object,
      required: true,
    },
    collapsed: Boolean,
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/containers';

.date-text {
  color: $mid-gray;
}
</style>
