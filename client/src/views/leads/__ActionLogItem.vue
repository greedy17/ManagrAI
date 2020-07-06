<template>
  <div class="action">
    <div class="item-list__item item-list__item--hover-effect">
      <div class="item-list__row" @click="$emit('item-click')">
        <div class="item-list__row-item--half">
          <img alt="icon" :src="require(`@/assets/images/checkmark.svg`)" class="icon" />
        </div>
        <div class="item-list__row-item--double">
          <strong>{{ log.meta.actionTypeRef.title }}</strong>
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
        <p>{{ log.meta.actionDetail }}</p>
        <p>
          Contacts:
          {{
            log.meta.linkedContactsRef &&
              log.meta.linkedContactsRef.map(c => c.full_name).join(', ')
          }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import LogItemArrowIcon from './__LogItemArrowIcon'

export default {
  name: 'ActionLogItem',
  components: { LogItemArrowIcon },
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
