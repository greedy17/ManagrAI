<template>
  <div class="activity-log-item">
    <NoteLogItem
      :log="log"
      :collapsed="!expanded"
      v-if="log.model === 'Note'"
      @item-click="emitToggleCollapse"
    />
    <CallNoteLogItem
      :log="log"
      :collapsed="!expanded"
      v-if="log.model === 'CallNote'"
      @item-click="emitToggleCollapse"
    />
    <ActionLogItem
      :log="log"
      :collapsed="!expanded"
      v-if="log.model === 'Action'"
      @item-click="emitToggleCollapse"
    />
    <EmailLogItem
      :log="log"
      :collapsed="!expanded"
      v-if="log.model === 'LeadEmail'"
      @item-click="emitToggleCollapse"
    />
    <LeadLogItem
      :log="log"
      :collapsed="!expanded"
      v-if="log.model === 'Lead'"
      @item-click="emitToggleCollapse"
    />
  </div>
</template>

<script>
import NoteLogItem from './__NoteLogItem'
import CallNoteLogItem from './__CallNoteLogItem'
import ActionLogItem from './__ActionLogItem'
import EmailLogItem from './__EmailLogItem'
import LeadLogItem from './__LeadLogItem'

export default {
  name: 'ActivityLogItem',
  components: { ActionLogItem, NoteLogItem, CallNoteLogItem, EmailLogItem, LeadLogItem },
  props: {
    log: {
      type: Object,
      required: true,
    },
    expanded: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      collapsed: true,
    }
  },
  methods: {
    emitToggleCollapse() {
      this.$emit('toggle-history-item', this.log.id)
    },
  },
}
</script>

<style lang="scss" scoped></style>
