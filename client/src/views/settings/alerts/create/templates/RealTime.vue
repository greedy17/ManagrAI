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
            src="@/assets/images/plusOne.svg"
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
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <h3>Stage Advanced</h3>
          <p class="active-workflow-small" v-if="advancedConfigActive">
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>

        <div class="card__body">
          <img style="height: 1.5rem; margin-right: 1rem" src="@/assets/images/logo.png" alt="" />
          <img
            style="height: 1rem; margin-right: 1rem; filter: invert(40%)"
            src="@/assets/images/plusOne.svg"
            alt=""
          />
          <img
            style="height: 1.25rem; margin-right: 1rem"
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

      <div class="card">
        <div class="card__header">
          <h3>Moved to Commit</h3>
          <p class="active-workflow-small" v-if="commitConfigActive">
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>

        <div class="card__body">
          <img style="height: 1.5rem; margin-right: 1rem" src="@/assets/images/logo.png" alt="" />
          <img
            style="height: 1rem; margin-right: 1rem; filter: invert(40%)"
            src="@/assets/images/plusOne.svg"
            alt=""
          />
          <img
            style="height: 1.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div class="card__footer">
          <button
            v-if="hasSalesforceIntegration && hasSlackIntegration"
            @click="goToCommit"
            class="orange_button"
          >
            View + Edit
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <h3>Close Date Pushed</h3>
          <p class="active-workflow-small" v-if="pushedConfigActive">
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>

        <div class="card__body">
          <img style="height: 1.5rem; margin-right: 1rem" src="@/assets/images/logo.png" alt="" />
          <img
            style="height: 1rem; margin-right: 1rem; filter: invert(40%)"
            src="@/assets/images/plusOne.svg"
            alt=""
          />
          <img
            style="height: 1.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div class="card__footer">
          <button
            v-if="hasSalesforceIntegration && hasSlackIntegration"
            @click="goToCloseDatePushed"
            class="orange_button"
          >
            View + Edit
          </button>
        </div>
      </div>

      <div class="card">
        <div class="card__header">
          <h3>Closed Won</h3>
          <p class="active-workflow-small" v-if="wonConfigActive">
            Active <img src="@/assets/images/configCheck.svg" alt="" />
          </p>
        </div>

        <div class="card__body">
          <img style="height: 1.5rem; margin-right: 1rem" src="@/assets/images/logo.png" alt="" />
          <img
            style="height: 1rem; margin-right: 1rem; filter: invert(40%)"
            src="@/assets/images/plusOne.svg"
            alt=""
          />
          <img
            style="height: 1.25rem; margin-right: 1rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div>

        <div class="card__footer">
          <button
            v-if="hasSalesforceIntegration && hasSlackIntegration"
            @click="goToClosedWon"
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
  {% comment %} mounted() {
    console.log(this.user)
  }, {% endcomment %}
  methods: {
    goToStageAdvanced() {
      this.$router.push({ name: 'StageAdvanced' })
    },
    goToCommit() {
      this.$router.push({ name: 'MovedToCommit' })
    },
    goToCloseDatePushed() {
      this.$router.push({ name: 'CloseDatePushed' })
    },
    goToClosedWon() {
      this.$router.push({ name: 'ClosedWon' })
    },
    goToZoomRecap() {
      this.$router.push({ name: 'ZoomRecap' })
    },
  },
  computed: {
    realtimeConfigs() {
      return Object.values(this.$store.state.user.slackAccount.realtimeAlertConfigs)
    },
    commitConfigActive() {
      for (let i = 0; i < this.realtimeConfigs.length; i++) {
        if (this.realtimeConfigs[i]['Moved to Commit']) {
          return true
        }
      }
    },
    advancedConfigActive() {
      for (let i = 0; i < this.realtimeConfigs.length; i++) {
        if (this.realtimeConfigs[i]['Stage Advanced']) {
          return true
        }
      }
    },
    pushedConfigActive() {
      for (let i = 0; i < this.realtimeConfigs.length; i++) {
        if (this.realtimeConfigs[i]['Close date pushed']) {
          return true
        }
      }
    },
    wonConfigActive() {
      for (let i = 0; i < this.realtimeConfigs.length; i++) {
        if (this.realtimeConfigs[i]['Closed Won']) {
          return true
        }
      }
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
  filter: invert(10%);
  margin-left: 0.5rem;
  margin-right: 0.5rem;
}
.alerts-page {
  margin-top: 3.5rem;
  font-family: $base-font-family;
}
.alert_cards {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  margin-top: 0.5rem;
  flex-wrap: wrap;
  width: 86vw;
}
.card:hover {
  box-shadow: 1px 2px 2px $very-light-gray;
}
.card {
  background-color: white;
  border: 1px solid #e8e8e8;
  border-radius: 0.5rem;
  width: 20vw;
  margin-right: 1rem;
  margin-bottom: 1rem;
  transition: all 0.25s;
  &__header {
    height: 2rem;
    padding: 1.25rem 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid $soft-gray;
    h3 {
      font-size: 14px;
      font-weight: 400 !important;
    }
  }
  &__body {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100px;
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
  font-size: 12px;
  letter-spacing: 0.25px;
  color: $gray;
}
.col {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  width: 82vw;
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