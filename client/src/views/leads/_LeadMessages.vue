<template>
  <div class="lead-messages">
    <div class="messages" v-if="!loading">
      <div :key="message.id" v-for="message in leadMessages.list" class="message">
        <Message :message="message" :lead="lead" />
      </div>
    </div>
    <div v-else>
      <ComponentLoadingSVG />
    </div>
  </div>
</template>

<script>
import ComponentLoadingSVG from '@/components/ComponentLoadingSVG'
import LeadMessage from '@/services/lead-messages'
import CollectionManager from '@/services/collectionManager'
import Message from '@/components/messages/Message'

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
    Message,
  },
  data() {
    return {
      loading: true,
      leadMessages: CollectionManager.create({
        ModelClass: LeadMessage,
        filters: {
          byLead: this.lead.id,
        },
      }),
    }
  },
  async created() {
    this.loading = true
    await this.refresh()
    this.loading = false
  },
  methods: {
    async refresh() {
      this.loading = true
      await this.leadMessages.refresh()
      this.loading = false
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/mixins/buttons';

.primary-button {
  @include primary-button;
}
</style>
