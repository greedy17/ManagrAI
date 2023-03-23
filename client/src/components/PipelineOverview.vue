<template>
  <div class="overview">
    <div class="header">
      <p>
        {{ activeWorkflow.title }}
      </p>

      <p style="margin-right: 8px">
        <img
          src="@/assets/images/left.svg"
          height="12px"
          alt=""
          style="margin-right: 4px; padding-top: 2px"
        />
        {{ activeWorkflow.length }}
      </p>
    </div>

    <div v-if="activeWorkflow">
      <section class="workflow" :key="i" v-for="(opp, i) in activeWorkflow">
        <div class="title">
          <div>
            <h4>
              {{ opp.Name }}
              <!-- <span>{{ activeWorkflowType }}</span> -->
            </h4>
            <p>Stage: {{ opp.StageName }}</p>
            <p>Close Date: {{ opp.CloseDate }}</p>
          </div>
        </div>
        <section class="button-section">
          <div>
            <button class="green-button">Update Record</button>
            <img src="@/assets/images/note.svg" height="14px" alt="" />
            <img src="@/assets/images/pipeline.svg" height="14px" alt="" />
          </div>
        </section>
      </section>
    </div>
  </div>
</template>

<script>
import { MeetingWorkflows } from '@/services/salesforce'
import { CollectionManager } from '@thinknimble/tn-models'
import AlertTemplate from '@/services/alerts/'
import User from '@/services/users'

export default {
  name: 'PipelineOverview',
  data() {
    return {
      activeNotis: false,
      workflows: [],
      users: CollectionManager.create({ ModelClass: User }),
    }
  },
  watch: {
    meetings: 'needsAction',
  },
  props: {
    activeWorkflow: {},
  },
  methods: {
    test(log) {
      console.log('log', log)
    },
    needsAction() {
      let NA = 0
      if (this.meetings.length) {
        for (let i = 0; i < this.meetings.length; i++) {
          !this.meetings[i].is_completed ? (NA += 1) : null

          NA === 0 ? (this.activeNotis = false) : (this.activeNotis = true)
        }
      }
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 $dark-green;
  }

  70% {
    transform: scale(1);
    box-shadow: 0 0 0 10px rgba(0, 0, 0, 0);
  }

  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(0, 0, 0, 0);
  }
}
.pulse {
  box-shadow: 0 0 0 0 $dark-green;
  transform: scale(1);
  animation: pulse 1.25s infinite;
}

.overview {
  padding: 0px 20px;
}

.title {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: flex-start;
  margin-bottom: 16px;
  width: 100%;

  div {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    margin-left: 16px;
    h4 {
      font-weight: 900;
      font-size: 14px;
      margin: 0;
      padding: 0;
      width: 36vw;
      display: flex;
      flex-direction: row;
      align-items: center;
      justify-content: space-between;

      span {
        // background-color: $off-white;
        color: $light-gray-blue;
        padding: 4px 8px;
        border-radius: 4px;
        margin-left: 12px;
        font-size: 13px;
        opacity: 0.9;
      }
    }

    p {
      font-weight: bold;
      font-size: 10px;
      color: $light-gray-blue;
      padding: 0;
      margin: 0;
      margin-top: 4px;
    }
  }
}
.green-button {
  @include primary-button();
  padding: 6px 12px;
  margin-right: 1rem;
  font-size: 12px;
}
.button-section {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  margin-left: 16px;
  border-bottom: 2px solid $soft-gray;
  padding-bottom: 16px;
  div {
    display: flex;
    flex-direction: row;
    align-items: center;

    img {
      margin-left: 8px;
    }
  }
}
.workflow {
  //   border-bottom: 2px solid $soft-gray;
  padding: 16px 0px 0px 0px;
  background-color: white;
  z-index: -1;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-left: 14px;
  position: sticky;
  background-color: white;
  z-index: 2;
  top: 0;
  p {
    font-size: 14px;
    span {
      color: $dark-green;
      padding: 2px 4px;
    }
  }
}
</style>