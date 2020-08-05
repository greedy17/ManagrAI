<template>
  <div class="lead-messages">
    <div class="messages" v-if="!loading">
      <div class="tab">
        <div class="tab__header">
          <ActionTabHeader
            v-for="(tab, index) in leadItem.linkedContactsRef"
            :key="'tab-' + index"
            :active="index === activeTab"
            :index="index"
            @update-active-tab="updateActiveTab"
          >
            {{ tab.full_name }}
          </ActionTabHeader>
        </div>
        <div class="tab__content">
          <template v-if="inbound.length > 0 || outbound.length > 0">
            <div class="incoming">
              <MessageContainer :direction="'Received'" :messages="inbound" />
            </div>
            <div class="outgoing">
              <MessageContainer :direction="'Sent'" :messages="outbound" />
            </div>
          </template>
          <template v-if="!this.activeTabContact.phone_number_1">
            <span class="muted">This Contact Has No Associated Number</span>
          </template>
          <template
            v-if="inbound.length < 1 && outbound.length < 1 && this.activeTabContact.phone_number_1"
          >
            <span class="muted">No Messages With this contact</span>
          </template>
        </div>
      </div>

      <!--       <div :key="message.id" v-for="message in leadMessages.list" class="message">
        <Message :message="message" :lead="lead" />
      </div> -->
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
import MessageContainer from '@/components/messages/MessageContainer'
import ActionTabHeader from '@/components/shared/ActionTabHeader'
import Messaging from '@/services/messages'

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
    MessageContainer,
    ActionTabHeader,
  },
  data() {
    return {
      loading: true,
      leadItem: this.lead,
      activeTab: 0,
      inbound: [],
      outbound: [],
      leadMessages: CollectionManager.create({
        ModelClass: LeadMessage,
        filters: {
          byLead: this.lead.id,
        },
      }),
    }
  },
  async created() {
    this.leadItem = this.getFreshLead
    this.loading = true
    await this.refresh()
    this.loading = false
    if (this.isTextConnected) {
      await this.getInboundMessages()
      await this.getOutbountMessages()
    }
  },
  computed: {
    activeTabContact() {
      return this.leadItem.linkedContactsRef[this.activeTab]
    },
    getFreshLead() {
      return this.lead
    },
    isTextConnected() {
      return this.$store.state.user.textConnected
    },
  },
  methods: {
    async getInboundMessages() {
      this.loading = true
      this.inbound = await Messaging.listMessages(
        this.activeTabContact.phone_number_1,
        this.isTextConnected,
      )
      this.loading = false
    },
    async getOutbountMessages() {
      this.loading = true
      this.outbound = await Messaging.listMessages(
        this.isTextConnected,
        this.activeTabContact.phone_number_1,
      )
      this.loading = false
    },
    async updateActiveTab(index) {
      if (this.activeTab != index) {
        this.activeTab = index
        this.inbound = []
        this.outbound = []
        if (this.activeTabContact.phone_number_1) {
          await this.getInboundMessages()
          await this.getOutbountMessages()
        }
      }
    },
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
@import '@/styles/variables';

.primary-button {
  @include primary-button;
}
.tab__header {
  min-height: 3rem;
  display: flex;
  flex-flow: row;
  overflow-x: scroll;
  max-width: 50rem;
}

.tab__content {
  display: flex;
  flex-flow: row;
  overflow-y: scroll;
  margin: 0 auto;
  padding: 1rem;

  > * {
    width: 20rem;
    margin: 1rem;
  }
}
</style>
