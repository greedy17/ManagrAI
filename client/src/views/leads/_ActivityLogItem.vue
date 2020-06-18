<template>
  <div class="activity-log-item">
    <NoteLogItem
      :log="log"
      :collapsed="collapsed"
      v-if="log.model === 'Note'"
      @item-click="toggleCollapsed"
    />
    <CallNoteLogItem
      :log="log"
      :collapsed="collapsed"
      v-if="log.model === 'CallNote'"
      @item-click="toggleCollapsed"
    />
    <ActionLogItem
      :log="log"
      :collapsed="collapsed"
      v-if="log.model === 'Action'"
      @item-click="toggleCollapsed"
    />
  </div>
</template>

<script>
import NoteLogItem from './__NoteLogItem'
import CallNoteLogItem from './__CallNoteLogItem'
import ActionLogItem from './__ActionLogItem'

export default {
  name: 'ActivityLogItem',
  components: { ActionLogItem, NoteLogItem, CallNoteLogItem },
  props: {
    log: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      collapsed: true,
    }
  },
  methods: {
    toggleCollapsed() {
      this.collapsed = !this.collapsed
    },
  },
}
</script>

<style lang="scss" scoped></style>
