<template>
  <div v-if="!tabs || !tabs.length" class="header">
    <div>
      <section v-if="!creating && !editing" class="left-margin row">
        <h3>
          {{ title }}
          <span v-if="titlesLength !== undefined && titlesLength !== null" class="gray-text"
            >: {{ titlesLength }}</span
          >
        </h3>

        <div v-if="!titlesLength" class="wrapper">
          <label class="icon workflow">
            <label class="tooltip">
              <span>
                <img src="@/assets/images/slackLogo.png" height="14px" alt="" />
                Send to Slack
              </span>
              <span>
                <img src="@/assets/images/listed.svg" height="14px" class="invert" />
                View List
              </span>
              <span>
                <img src="@/assets/images/edit.svg" height="14px" alt="" class="invert" />
                Edit Workflow
              </span>
              <span>
                <img src="@/assets/images/toggle.svg" height="16px" alt="" class="invert" />
                Send to Slack
              </span>
            </label>
            <span>?</span>
          </label>
        </div>
      </section>

      <h3 v-else @click="cancel" class="left-margin-s">
        <img
          style="margin-right: 4px; filter: invert(40%)"
          src="@/assets/images/left.svg"
          height="13px"
          alt=""
        />
        Back
      </h3>
    </div>

    <div v-if="editing">
      <span class="gray-text">{{ subtitle }}</span>
    </div>

    <div v-if="isPaid">
      <button v-if="!creating && !editing" class="green_button right-margin" @click="buttonAction">
        {{ buttonText }}
      </button>

      <button
        @click="saveItem"
        :disabled="!canSave"
        class="green_button right-margin"
        :class="canSave ? 'pulse' : ''"
        v-else-if="creating"
      >
        {{ buttonText }}
      </button>

      <div v-else>
        <button @click="deleteItem(deleteId)" class="delete">Delete</button>
        <button @click="updateItem" style="margin-left: 8px" class="green_button right-margin">
          Update
        </button>
      </div>
    </div>

    <div v-else>
      <div class="tooltip" v-if="!creating && !editing">
        <button disabled class="green_button right-margin center-row">
          {{ buttonText }}
          <img
            class="shimmer"
            style="filter: invert(40%)"
            src="@/assets/images/lock.svg"
            height="16px"
            alt=""
          />
        </button>
        <small class="tooltiptext">Upgrade to <strong>Startup Plan</strong></small>
      </div>

      <button
        @click="saveItem"
        :disabled="!canSave"
        class="green_button right-margin"
        :class="canSave ? 'pulse' : ''"
        v-else-if="creating"
      >
        {{ buttonText }}
      </button>

      <div v-else>
        <button @click="deleteItem(deleteId)" class="delete">Delete</button>
        <button @click="updateItem" style="margin-left: 8px" class="green_button right-margin">
          Update
        </button>
      </div>
    </div>
  </div>
  <div v-else class="alerts-header">
    <div v-if="title">
      <h3 class="left-margin">
        {{ title }}
        <span v-if="titlesLength !== undefined && titlesLength !== null" class="gray-text"
          >: {{ titlesLength }}</span
        >
      </h3>
    </div>
    <!-- if tabs and tabs length, show tabs -->
    <section v-for="tab in tabs" :key="tab.name" class="row__ light-gray">
      <p @click="tab.function" :class="tab.classLogic ? 'green' : ''">
        {{ tab.name }}
      </p>
    </section>
    <div class="save-refresh-section">
      <div v-if="page === 'forms'">
        <button v-if="!saving" class="img-button img-border" @click="refreshForms">
          <img src="@/assets/images/refresh.svg" />
        </button>
        <PulseLoadingSpinnerButton
          v-else
          @click="refreshForms"
          class="img-button"
          text="Refresh"
          :loading="saving"
          ><img src="@/assets/images/refresh.svg"
        /></PulseLoadingSpinnerButton>
      </div>
      <!-- Save Form -->
      <button v-if="!saving" @click="onSave" class="save">{{ buttonText }}</button>
      <div v-else>
        <PipelineLoader />
      </div>
    </div>
  </div>
</template>


<script>
import PulseLoadingSpinnerButton from '@thinknimble/pulse-loading-spinner-button'
import PipelineLoader from './PipelineLoader'

export default {
  name: 'AlertsHeader',
  components: {
    PulseLoadingSpinnerButton,
    PipelineLoader,
  },
  props: {
    title: { type: String },
    tabs: { type: Array },
    page: { type: String },
    saving: { type: Boolean },
    currentAlert: { type: Object },
    creating: { type: Boolean },
    editing: { type: Boolean },
    canSave: { type: Boolean },
    isPaid: { type: Boolean },
    buttonText: { type: String },
    titlesLength: { type: Number },
    subtitle: { type: String },
    deleteId: { type: String },
    buttonText: { type: String },
  },
  data() {
    return {}
  },
  methods: {
    refreshForms() {
      this.$emit('refresh-forms')
    },
    onSave() {
      this.$emit('on-save')
    },
    saveItem() {
      this.$emit('save-item')
    },
    updateItem() {
      this.$emit('update-item')
    },
    deleteItem(id) {
      this.$emit('delete-item', id)
    },
    cancel() {
      this.$emit('cancel')
    },
    buttonAction() {
      this.$emit('button-action')
    },
  },
}
</script>


<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';

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
// .pulse {
//   box-shadow: 0 0 0 0 $dark-green;
//   transform: scale(1);
//   animation: pulse 1.25s infinite;
// }
.header {
  position: fixed;
  z-index: 100;
  margin-left: -12px;
  top: 0;
  background-color: $white;
  width: 96vw;
  border-bottom: 1px solid $soft-gray;
  padding-top: 8px;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  // gap: 24px;

  h3 {
    font-size: 16px;
    font-weight: 400;
    letter-spacing: 0.75px;
    line-height: 1.2;
    cursor: pointer;
  }
}
.left-margin {
  margin-left: 30px;
}
.left-margin-s {
  margin-left: 16px;
}
.row {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}
.row__ {
  display: flex;
  flex-direction: row;
  justify-content: flex-start;
  align-items: center;
  gap: 24px;
  margin-left: 16px;
  letter-spacing: 0.75px;
  font-size: 14px;
}
.light-gray {
  color: $light-gray-blue;
  cursor: pointer;
}
.green {
  color: $dark-green !important;
  background-color: $white-green;
  padding: 6px 8px;
  border-radius: 4px;
  font-weight: bold;
}
.save-refresh-section {
  display: flex;
}
.img-button {
  background-color: transparent;
  padding: 4px 6px;
  margin-right: 0.5rem;
  border: none;
}
.invert {
  filter: invert(60%);
}
.img-border {
  border: 1px solid #eeeeee;
  padding: 4px 6px 3px 6px;
  border-radius: 6px;
  background-color: white;
}
.save {
  padding: 8px 20px;
  font-size: 13px;
  background-color: $dark-green;
  color: white;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
}
.gray-text {
  color: $light-gray-blue;
}
.green_button {
  color: white;
  background-color: $dark-green;
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 12px;
  border: none;
  cursor: pointer;
  text-align: center;
}
.green_button:disabled {
  background-color: $soft-gray;
  color: $gray;
}
.right-margin {
  margin-right: 40px;
}
.delete {
  background-color: $coral;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  padding: 8px 16px;
  margin-left: 8px;
}
.center-row {
  display: flex;
  flex-direction: row;
  align-items: center;
}
.tooltip {
  position: relative;
  display: inline-block;
}

/* Tooltip text */
.tooltip .tooltiptext {
  visibility: hidden;
  width: 140px;
  background-color: black;
  color: #fff;
  text-align: center;
  padding: 5px 0;
  border-radius: 6px;
  opacity: 0.7;

  /* Position the tooltip text - */
  position: absolute;
  z-index: 1;
  top: 5px;
  right: 105%;
}

/* Show the tooltip text when you mouse over the tooltip container */
.tooltip:hover .tooltiptext {
  visibility: visible;
}
.shimmer {
  display: inline-block;
  -webkit-mask: linear-gradient(-60deg, #000 30%, #0005, #000 70%) right/300% 100%;
  background-repeat: no-repeat;
  animation: shimmer 2.5s infinite;
  max-width: 200px;
}

.wrapper {
  padding: 0;
  margin: 0;
  margin-top: -4px;
}

.wrapper .icon {
  position: relative;
  background: #ffffff;
  border-radius: 50%;
  padding: 10px;
  outline: 1px solid red;
  margin: 20px 12px 0px 12px;
  width: 18px;
  height: 18px;
  font-size: 13px;
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
  outline: 1px solid $mid-gray;
  // box-shadow: 0 2px 2px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.wrapper .tooltip {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  width: 250px;
  height: auto;
  gap: 12px;
  position: absolute;
  top: 0;
  font-size: 14px;
  background: #ffffff;
  color: #ffffff;
  padding: 8px 12px 0px 12px;
  border-radius: 5px;
  box-shadow: 0 10px 10px rgba(0, 0, 0, 0.1);
  opacity: 0;
  pointer-events: none;
  line-height: 1.5;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);

  span {
    border-bottom: 1px solid $very-light-gray;
    width: 100%;
    padding-bottom: 8px;

    display: flex;
    align-items: center;

    img {
      margin-right: 8px;
    }
  }
  span:last-of-type {
    border-bottom: none;
  }
}

.wrapper .tooltip::before {
  position: absolute;
  content: '';
  height: 8px;
  width: 8px;
  background: #ffffff;
  top: -3px;
  left: 50%;
  transform: translate(-50%) rotate(45deg);
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.wrapper .icon:hover .tooltip {
  top: 36px;
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
}

.wrapper .icon:hover span,
.wrapper .icon:hover .tooltip {
  text-shadow: 0px -1px 0px rgba(0, 0, 0, 0.1);
}

.wrapper .workflow:hover,
.wrapper .workflow:hover .tooltip,
.wrapper .workflow:hover .tooltip::before {
  background: $grape;
  color: #ffffff;
}
</style>