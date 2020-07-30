<template>
  <div class="lead-messages">
    <div class="messages">
      <div :key="message.id" v-for="message in leadMessages.list" class="message">
        Message Sent From:
        {{
          message.direction == 'SENT'
            ? message.createdByRef.fullName
            : 'number associated with ' + message.linkedContactsRef.map(c => c.fullName)
        }}
        Message:{{ message.body }} Status:{{ message.status }}
      </div>
    </div>
  </div>
</template>

<script>
import ComponentLoadingSVG from '@/components/ComponentLoadingSVG'
import LeadMessage from '@/services/lead-messages'
import CollectionManager from '@/services/collectionManager'

export default {
  name: 'LeadMessages',
  props: {
    lead: {
      type: Object,
      required: true,
    },
  },
  components: {
    ComponentLoadingSVG,
  },
  data() {
    return {
      leadMessages: CollectionManager.create({
        ModelClass: LeadMessage,
        filters: {},
      }),
    }
  },
  created() {
    this.leadMessages.refresh()
  },
  methods: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';

.primary-button {
  @include primary-button;
}
</style>
