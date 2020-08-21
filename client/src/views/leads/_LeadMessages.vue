<template>
  <div class="lead-messages" v-if="!!isTextConnected && activeTabContact">
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
          <template v-if="activeTabContact && (inbound.length > 0 || outbound.length > 0)">
            <div class="incoming">
              <MessageContainer :direction="'Received'" :messages="inbound" />
            </div>
            <div class="outgoing">
              <MessageContainer :direction="'Sent'" :messages="outbound" />
            </div>
          </template>

          <template v-if="!activeTabContact.phone_number_1">
            <span class="muted">This Contact Has No Associated Number</span>
          </template>
          <template
            v-if="
              inbound.length < 1 &&
                outbound.length < 1 &&
                activeTabContact &&
                activeTabContact.phone_number_1
            "
          >
            <span class="muted">No Messages With this contact</span>
          </template>
        </div>
      </div>
    </div>
    <div v-else>
      <ComponentLoadingSVG />
    </div>
  </div>

  <div v-else class="lead-messages">
    <span v-if="!isTextConnected" class="muted">
      Please Enable Text Integration in your account settings
    </span>
    <template v-if="!activeTabContact">
      <span class="muted">This Lead Has No Associated Contacts</span>
    </template>
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
      loading: false,
      leadItem: this.lead,
      activeTab: 0,
      inbound: [],
      outbound: [],
    }
  },
  async created() {
    this.leadItem = this.getFreshLead

    if (this.isTextConnected && this.activeTabContact) {
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
      try {
        if (this.activeTabContact && this.activeTabContact.phone_number_1) {
          this.inbound = await Messaging.listMessages(
            this.activeTabContact.phone_number_1,
            this.isTextConnected,
          )
        }
      } catch {
        this.$Alert.alert({
          type: 'error',
          message: `<h4> There was an error retrieving these messages</h4>`,
          timeout: 5000,
        })
      } finally {
        this.loading = false
      }
    },
    async getOutbountMessages() {
      this.loading = true

      try {
        if (this.activeTabContact && this.activeTabContact.phone_number_1) {
          this.outbound = await Messaging.listMessages(
            this.isTextConnected,
            this.activeTabContact.phone_number_1,
          )
        }
      } catch {
        this.$Alert.alert({
          type: 'error',
          message: `<h4> There was an error retrieving these messages</h4>`,
          timeout: 5000,
        })
      } finally {
        this.loading = false
      }
    },
    async updateActiveTab(index) {
      if (this.activeTab != index) {
        this.activeTab = index
        this.inbound = []
        this.outbound = []

        if (this.activeTabContact && this.activeTabContact.phone_number_1) {
          await this.getInboundMessages()
          await this.getOutbountMessages()
        }
      }
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
