<template>
  <div class="alerts-page">
    <div class="col">
      <h3>Instant Updates</h3>
      <p class="sub__">Activate the workflows that are relevant to you</p>
    </div>

    <div class="alert_cards">
      <div class="card">
        <div class="card__header">
          <h3>Meeting Recaps</h3>
        </div>
        <div class="card__body">
          <img style="height: 1.5rem; margin-right: 0.5rem" src="@/assets/images/zoom.png" alt="" />
          <img
            style="height: 1rem; margin-right: 0.5rem"
            src="@/assets/images/plusOne.png"
            class="filter-plus"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/gmailCal.png"
            alt=""
          />
        </div>
        <div class="card__footer">
          <button
            v-if="hasSlackIntegration && !recapChannel"
            @click="goToZoomRecap"
            class="orange_button"
          >
            Activate
          </button>

          <p class="active-workflow" v-else-if="recapChannel">
            Active <img src="@/assets/images/configCheck.png" alt="" />
          </p>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <h3>Deal Movement</h3>
          <p class="active-workflow-small" v-if="hasRealTimeConfigs">
            Active <img src="@/assets/images/configCheck.png" alt="" />
          </p>
        </div>

        <div class="card__body">
          <img
            style="height: 1.5rem; margin-right: 1rem"
            src="@/assets/images/slackLogo.png"
            alt=""
          />
          <img
            style="height: 1rem; margin-right: 1rem; filter: invert(60%)"
            src="@/assets/images/plusOne.png"
            alt=""
          />
          <img
            style="height: 1.5rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div class="card__footer">
          <button
            v-if="hasSalesforceIntegration && hasSlackIntegration"
            @click="goToStageAdvanced"
            class="orange_button"
          >
            View + Edit
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/**
 * Services
 */

import AlertTemplate, { AlertTemplateForm } from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { CollectionManager } from '@thinknimble/tn-models'
import { SObjectField, NON_FIELD_ALERT_OPTS, SOBJECTS_LIST } from '@/services/salesforce'
import User from '@/services/users'
import { SlackListResponse } from '@/services/slack'

export default {
  name: 'RealTime',
  data() {
    return {
      channelOpts: new SlackListResponse(),
      savingTemplate: false,
      listVisible: true,
      dropdownVisible: true,
      NON_FIELD_ALERT_OPTS,
      stringRenderer,
      SOBJECTS_LIST,
      alertTemplateForm: new AlertTemplateForm(),
      selectedBindings: [],
      fields: CollectionManager.create({ ModelClass: SObjectField }),
      users: CollectionManager.create({ ModelClass: User }),
      templates: CollectionManager.create({ ModelClass: AlertTemplate }),
    }
  },
  async created() {
    this.templates.refresh()
  },
  methods: {
    goToStageAdvanced() {
      this.$router.push({ name: 'DealMovement' })
    },
    goToZoomRecap() {
      this.$router.push({ name: 'ZoomRecap' })
    },
  },
  computed: {
    hasRealTimeConfigs() {
      return !!this.user.slackAccount.realtimeAlertConfigs
    },
    hasSalesforceIntegration() {
      return !!this.$store.state.user.salesforceAccount
    },
    hasSlackIntegration() {
      return !!this.$store.state.user.slackRef
    },
    recapChannel() {
      return this.$store.state.user.slackAccount.recapChannel
    },
    user() {
      return this.$store.state.user
    },
    selectedResourceType: {
      get() {
        return this.alertTemplateForm.field.resourceType.value
      },
      set(val) {
        this.alertTemplateForm.field.resourceType.value = val
      },
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/layout';
@import '@/styles/containers';
@import '@/styles/forms';
@import '@/styles/emails';
@import '@/styles/sidebars';
@import '@/styles/mixins/buttons';
@import '@/styles/mixins/utils';
@import '@/styles/buttons';

@keyframes bounce {
  0% {
    transform: translateY(0);
  }
  100% {
    transform: translateY(-6px);
  }
}
.active-workflow {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 1.5rem;
  margin-right: 1rem;
  border: 1px solid $soft-gray;
  background-color: white;
  border-radius: 0.3rem;
  color: $dark-green;
  font-size: 12px;
  cursor: text;
  img {
    height: 1rem;
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
    margin-left: 0.75rem;
    margin-top: 0.1rem;
  }
}
.active-workflow-small {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 0.3rem 0.4rem;
  border: 1px solid $soft-gray;
  background-color: white;
  border-radius: 0.3rem;
  color: $dark-green;
  font-size: 11px;
  cursor: text;
  img {
    height: 0.8rem;
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
    margin-left: 0.75rem;
    margin-top: 0.1rem;
  }
}
.filter-plus {
  filter: invert(90%);
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}
.alerts-page {
  margin-left: 10vw;
  margin-top: 3.5rem;
}
.alert_cards {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  margin-top: 0.5rem;
  flex-wrap: wrap;
}
.card:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
}
.card {
  background-color: white;
  border: 1px solid #e8e8e8;
  border-radius: 0.5rem;
  width: 24vw;
  margin-right: 1rem;
  margin-bottom: 1rem;
  transition: all 0.25s;
  &__header {
    height: 2rem;
    padding: 1.25rem 1rem;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid $soft-gray;
  }
  &__body {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 5rem;
    font-size: 13px;
  }
  &__footer {
    display: flex;
    align-items: center;
    height: 2rem;
    font-size: 14px;
    justify-content: space-evenly;
  }
}
.sub__ {
  font-size: 14px;
  margin-top: -0.5rem;
  color: $gray;
}
.col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-left: 0.75rem;
  margin-top: 1rem;
}
.orange_button {
  background-color: $dark-green;
  color: white;
  font-size: 14px;
  border-radius: 0.3rem;
  border: 2px solid $dark-green;
  padding: 0.25rem 1.5rem;
  cursor: pointer;
}
</style>