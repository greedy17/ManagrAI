<template>
  <div class="alerts-page">
    <div v-if="!showLoader" class="deal-header">
      <div class="col">
        <h2 @click="log" style="color: black; margin-top: -0.5rem" class="title">Deal Movement</h2>
        <p style="color: #5d5e5e" class="sub__">Activate workflows related to deal movement</p>
      </div>

      <button @click="$router.push({ name: 'RealTime' })" class="back-button">
        <img class="invert" src="@/assets/images/back.svg" alt="" />
        Back to workflows
      </button>
    </div>

    <div class="center-loader" v-if="showLoader">
      <Loader />
    </div>

    <div v-if="!showLoader" class="row">
      <div v-if="!advancedConfigActive" @click="onAdvancing" class="stage-item">
        <p>Stage Advanced</p>
        <button class="plus_button">
          <img src="@/assets/images/add.svg" alt="" />
        </button>
      </div>
      <div v-else class="added-item">
        <p>Stage Advanced</p>
        <button style="cursor: auto" class="plus_button">
          <img src="@/assets/images/configCheck.svg" class="filtered" alt="" />
        </button>
      </div>

      <div v-if="!commitConfigActive" @click="onCommit" class="stage-item">
        <p>Moved to Commit</p>
        <button class="plus_button">
          <img src="@/assets/images/add.svg" alt="" />
        </button>
      </div>
      <div v-else class="added-item">
        <p>Moved to Commit</p>
        <button style="cursor: auto" class="plus_button">
          <img src="@/assets/images/configCheck.svg" class="filtered" alt="" />
        </button>
      </div>

      <div v-if="!pushedConfigActive" @click="onPushing" class="stage-item">
        <p>Close Date Pushed</p>
        <button class="plus_button">
          <img src="@/assets/images/add.svg" alt="" />
        </button>
      </div>
      <div v-else class="added-item">
        <p>Close Date Pushed</p>
        <button style="cursor: auto" class="plus_button">
          <img src="@/assets/images/configCheck.svg" class="filtered" alt="" />
        </button>
      </div>

      <div v-if="!wonConfigActive" @click="onWinning" class="stage-item">
        <p>Closed Won</p>
        <button class="plus_button">
          <img src="@/assets/images/add.svg" alt="" />
        </button>
      </div>
      <div v-else class="added-item">
        <p>Closed Won</p>
        <button style="cursor: auto" class="plus_button">
          <img src="@/assets/images/configCheck.svg" class="filtered" alt="" />
        </button>
      </div>
    </div>

    <div
      v-if="
        !pushedConfigActive &&
        !advancedConfigActive &&
        !commitConfigActive &&
        !commit &&
        !pushing &&
        !advancing &&
        !showLoader
      "
      style="margin-top: 10%"
    >
      <h1 class="bouncy" style="color: #5d5e5e; font-weight: bold; text-align: center">0</h1>
      <h6 style="font-weight: bold; color: #5d5e5e; text-align: center">
        Nothing here, add a workflow to get started.. (o^^)o
      </h6>
    </div>

    <div v-if="!showLoader" class="alert-row">
      <div v-if="advancedConfigActive && !advancing" class="added-collection">
        <div class="added-collection__header">
          <p class="title">Stage Advanced</p>
          <span class="active">active</span>
        </div>
        <section class="added-collection__body">
          <p>Recieve alerts when deals advances to your selected stage</p>
        </section>
        <section class="added-collection__footer">
          <div class="edit" @click="onAdvancing">
            <img src="@/assets/images/edit.svg" class="invert" alt="" />
          </div>
        </section>
      </div>

      <div v-if="commitConfigActive && !commit" class="added-collection">
        <div class="added-collection__header">
          <p class="title">Moved to Commit</p>
          <span class="active">active</span>
        </div>
        <section class="added-collection__body">
          <p>Recieve alerts when deals move to commit.</p>
        </section>
        <section class="added-collection__footer">
          <div class="edit" @click="onCommit">
            <img src="@/assets/images/edit.svg" class="invert" alt="" />
          </div>
        </section>
      </div>

      <div v-if="pushedConfigActive && !pushing" class="added-collection">
        <div class="added-collection__header">
          <p class="title">Close Date Pushed</p>
          <span class="active">active</span>
        </div>
        <section class="added-collection__body">
          <p>Recieve alerts when Close Date's are pushed into a new month.</p>
        </section>
        <section class="added-collection__footer">
          <div class="edit" @click="onPushing">
            <img src="@/assets/images/edit.svg" class="invert" alt="" />
          </div>
        </section>
      </div>

      <div v-if="wonConfigActive && !winning" class="added-collection">
        <div class="added-collection__header">
          <p class="title">Closed Won</p>
          <span class="active">active</span>
        </div>
        <section class="added-collection__body">
          <p>Recieve alerts when deals are closed.</p>
        </section>
        <section class="added-collection__footer">
          <div class="edit" @click="onWinning">
            <img src="@/assets/images/edit.svg" class="invert" alt="" />
          </div>
        </section>
      </div>

      <transition name="fade">
        <div v-if="advancing">
          <StageAdvanced></StageAdvanced>
        </div>
      </transition>

      <transition name="fade">
        <div v-if="commit">
          <MovedToCommit></MovedToCommit>
        </div>
      </transition>

      <transition name="fade">
        <div v-if="pushing">
          <CloseDatePushed></CloseDatePushed>
        </div>
      </transition>

      <transition name="fade">
        <div v-if="winning">
          <ClosedWon></ClosedWon>
        </div>
      </transition>
    </div>
  </div>
</template>

<script>
/**
 * Components
 * */
// Pacakges
import 'quill/dist/quill.core.css'
import 'quill/dist/quill.snow.css'
import 'quill/dist/quill.bubble.css'

//Internal
import MovedToCommit from '@/views/settings/alerts/create/templates/MovedToCommit'
import CloseDatePushed from '@/views/settings/alerts/create/templates/CloseDatePushed'
import StageAdvanced from '@/views/settings/alerts/create/templates/StageAdvanced'
import ClosedWon from '@/views/settings/alerts/create/templates/ClosedWon'

/**
 * Services
 */

import AlertTemplate, { AlertTemplateForm } from '@/services/alerts/'
import { stringRenderer } from '@/services/utils'
import { CollectionManager } from '@thinknimble/tn-models'
import {
  SObjectField,
  NON_FIELD_ALERT_OPTS,
  SOBJECTS_LIST,
} from '@/services/salesforce'
import User from '@/services/users'
import { SlackListResponse } from '@/services/slack'

export default {
  name: 'DealMovement',
  components: {
    Loader: () => import(/* webpackPrefetch: true */ '@/components/Loader'),
    MovedToCommit,
    CloseDatePushed,
    StageAdvanced,
    ClosedWon,
  },
  data() {
    return {
      channelOpts: new SlackListResponse(),
      savingTemplate: false,
      listVisible: true,
      dropdownVisible: true,
      advancing: false,
      commit: false,
      pushing: false,
      winning: false,
      showLoader: true,
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
    log() {
      console.log(this.realtimeConfigs)
    },
    onAdvancing() {
      this.advancing = !this.advancing
    },
    onCommit() {
      this.commit = !this.commit
    },
    onPushing() {
      this.pushing = !this.pushing
    },
    onWinning() {
      this.winning = !this.winning
    },
  },
  mounted() {
    setTimeout(() => {
      this.showLoader = false
    }, 300)
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
.bouncy {
  animation: bounce 0.2s infinite alternate;
}
.deal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-direction: row;
  padding-right: 5vw;
}
.back-button {
  font-size: 14px;
  color: $dark-green;
  background-color: transparent;
  display: flex;
  align-items: center;
  border: none;
  cursor: pointer;
  margin: 1rem 0rem 0rem 0rem;

  img {
    height: 1rem;
    margin-right: 0.5rem;
    filter: brightness(0%) saturate(100%) invert(63%) sepia(31%) saturate(743%) hue-rotate(101deg)
      brightness(93%) contrast(89%);
  }
}
.center-loader {
  display: flex;
  justify-content: center;
  flex-direction: column;
  align-items: center;
  height: 60vh;
}
.edit {
  border: 1px solid #e8e8e8;
  background-color: transparent;
  border-radius: 0.25rem;
  padding: 0.25rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  img {
    height: 1rem;
    filter: invert(80%);
  }
}

.plus_button {
  border: none;
  background-color: transparent;
  border-radius: 50%;
  padding: 0.2rem;
  margin-left: 0.25rem;
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: bold;
}
.alert-row {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  justify-content: flex-start;
  padding: 0;
}
.filtered {
  filter: invert(33%) sepia(52%) saturate(2452%) hue-rotate(130deg) brightness(68%) contrast(80%);
  height: 1.2rem;
}
.invert {
  filter: invert(80%);
}
.alerts-page {
  margin-top: 4.5rem;
}
.stage-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 0rem 0.75rem;
  margin-right: 1rem;
  box-shadow: 1px 3px 7px $very-light-gray;
  border: 1px solid $soft-gray;
  border-radius: 7px;
  color: $base-gray;
  cursor: pointer;
  font-size: 12px;
}
.added-collection {
  background-color: white;
  box-shadow: 2px 2px 3px $very-light-gray;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-top: 2rem;
  width: 20vw;
  max-height: 27vh;
  margin-right: 2vw;
  &__header {
    max-height: 3rem;
    display: flex;
    align-items: center;
    justify-content: flex-start;
    border-bottom: 3px solid $soft-gray;
  }
  &__body {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 4rem;
    font-size: 13px;
  }
  &__footer {
    display: flex;
    align-items: flex-end;
    height: 3rem;
    justify-content: flex-end;
  }
}
.added-item {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  padding: 0rem 0.75rem;
  margin-right: 1rem;
  box-shadow: 1px 1px 1px $very-light-gray;
  background-color: white;
  border-radius: 0.2rem;
  color: $dark-green;
  font-size: 12px;
  cursor: not-allowed;
}
.active {
  background-color: $lighter-green;
  border-radius: 0.2rem;
  border: none;
  padding: 0.25rem;
  font-size: 10px;
  margin-left: 0.5rem;
  color: $darker-green;
}
.sub__ {
  font-size: 13px;
  margin-top: -0.5rem;
  color: $very-light-gray;
}
.col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-left: 0.75rem;
  margin-top: 1rem;
}
.row {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: flex-start;
  padding: 0.5rem 0rem;
  border-bottom: 2px solid $soft-gray;
  width: 98vw;
}
</style>