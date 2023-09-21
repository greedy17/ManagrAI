<template>
  <div class="sync">
    <!-- <div class="card">
      <h2>Sync CRM</h2>
      <button class="white-green-button"><img src="@/assets/images/cycle.svg" class="img-height" />Sync</button>
    </div> -->
    <!-- <div class="card">
      <h2>Sync Calendar</h2>
      <button class="white-green-button"><img src="@/assets/images/cycle.svg" class="img-height" />Sync</button>
    </div> -->
    <div class="card">
      <div class="card__header">
        <img
          v-if="userCRM === 'SALESFORCE'"
          src="@/assets/images/salesforce.png"
          style="margin-right: 16px; height: 40px"
        />
        <img
          v-else-if="userCRM === 'HUBSPOT'"
          src="@/assets/images/hubspot-single-logo.svg"
          style="height: 40px"
        />
      </div>
      <div class="card__body">
        <div style="display: flex">
          <h3 class="card__title">Sync {{ userCRMFormatted }}</h3>
        </div>
        <div class="card-text-container">
          <p class="card-text">Click sync to get the lastest data from {{ userCRMFormatted }}</p>
        </div>
        <div class="sep-button-container">
          <div class="separator"></div>
          <button
            class="long-button"
            style="margin-right: 0; margin-top: 1rem; margin-bottom: 0.5rem"
            @click="refreshCRM"
          >
            <img src="@/assets/images/cycle.svg" class="img-height" style="" />
            Sync
          </button>
        </div>
      </div>
    </div>
    <!-- <div class="card">
      <div class="card__header">
        <img src="@/assets/images/gmailCal.png" style="margin-right: 16px; height: 40px" />
        <img src="@/assets/images/outlookMail.png" style="height: 40px" />
      </div>
      <div class="card__body">
        <div style="display: flex">
          <h3 class="card__title">
            Sync Calendar
          </h3>
        </div>
        <div class="card-text-container">
          <p class="card-text">Click sync to get the lastest meeting data from your calendar</p>
        </div>
        <div class="sep-button-container">
          <div class="separator"></div>
          <button class="long-button" style="margin-right: 0; margin-top: 1rem; margin-bottom: 0.5rem;" @click="refreshCalEvents">
            <img 
              src="@/assets/images/cycle.svg" 
              class="img-height"
              style=""
            />
            Sync 
          </button>
        </div>
      </div>
    </div> -->
  </div>
</template>

<script>
// import SlackOAuth from '@/services/slack'
import User from '@/services/users'
import { CRMObjects } from '@/services/crm'

export default {
  name: 'ConfigureSync',
  components: {},
  props: {},
  data() {
    return {
      pulseLoadingForms: false,
      pulseLoadingCal: false,
    }
  },
  created() {},
  methods: {
    async refreshCRM() {
      this.pulseLoadingForms = true
      const res = await CRMObjects.api.resourceSync()
      setTimeout(() => {
        this.pulseLoadingForms = false
        this.$store.dispatch('refreshCurrentUser')
        if (res.success) {
          this.$toast('Sync complete', {
            timeout: 2000,
            position: 'top-left',
            type: 'success',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        } else {
          this.$toast('Could not sync your CRM', {
            timeout: 2000,
            position: 'top-left',
            type: 'error',
            toastClassName: 'custom',
            bodyClassName: ['custom'],
          })
        }
      }, 300)
    },
    // async manualSync() {
    //   try {
    //     await CRMObjects.api.resourceSync()
    //     this.$toast('Sync complete', {
    //       timeout: 2000,
    //       position: 'top-left',
    //       type: 'success',
    //       toastClassName: 'custom',
    //       bodyClassName: ['custom'],
    //     })
    //   } catch (e) {
    //     this.$toast('Error syncing your resources, refresh page', {
    //       timeout: 2000,
    //       position: 'top-left',
    //       type: 'error',
    //       toastClassName: 'custom',
    //       bodyClassName: ['custom'],
    //     })
    //   } finally {
    //     this.$store.dispatch('refreshCurrentUser')
    //     setTimeout(() => {
    //       this.loading = false
    //     }, 100)
    //   }
    // },
    async refreshCalEvents() {
      this.pulseLoadingCal = true
      try {
        const res = await User.api.refreshCalendarEvents()
        setTimeout(() => {
          this.pulseLoadingCal = false
        }, 300)
      } catch (e) {
        console.log('Error in refreshCalEvents: ', e)
      }
    },
  },
  computed: {
    userCRM() {
      return this.$store.state.user.crm
    },
    userCRMFormatted() {
      return this.userCRM[0] + this.userCRM.slice(1, this.userCRM.length).toLowerCase()
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';
@import '@/styles/modals';

.sync {
  display: flex;
  justify-content: flex-start;
  margin-left: 1.5rem;
  margin-top: 5.5rem;
  width: 55vw;
}
// .card {
//   display: flex;
//   flex-direction: column;
//   align-items: center;
//   width: 25vw;
// }
.card {
  background-color: $white;
  // padding: 16px 24px;
  padding: 0.5rem 0.75rem;
  border: 1px solid $soft-gray;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  margin-right: 1rem;
  margin-bottom: 1rem;
  // width: 420px;
  // width: 320px;
  width: 18.5vw;
  min-height: 144px;
  transition: all 0.25s;

  &__header {
    display: flex;
    align-items: center;
    // justify-content: center;
    padding: 4px 0px;
    border-radius: 6px;
    margin-left: 12px;

    img {
      margin: 0;
      height: 25px;
    }
  }

  &__body {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    margin-left: 12px;
    h3 {
      margin-top: 0.2rem;
      margin-bottom: 0;
      // margin: 0;
      padding: 0;
      font-size: 16px;
    }
    p {
      font-size: 12px;
    }
  }
}
.card-img-border {
  // padding: 5px;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 40px;
  width: 40px;
  // border: 1px solid $soft-gray;
  border-radius: 4px;
  margin-right: 0.15rem;
}
.white-green-button {
  @include white-button();
  display: flex;
  align-items: center;
}
.img-height {
  height: 11px;
  margin-right: 0.5rem;
  filter: brightness(0%) invert(64%) sepia(8%) saturate(2746%) hue-rotate(101deg) brightness(97%)
    contrast(82%);
}
.card-text-container {
  min-height: 3.5rem;
  display: flex;
  align-items: center;
}
.card-text {
  font-size: 14px;
  color: $light-gray-blue;
  margin-top: 0.5rem;
  // text-align: center;
}
.sep-button-container {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}
.separator {
  border-top: 1px solid $soft-gray;
  width: 15vw;
  // margin: 0rem 0 0.1rem 0;
}
.long-button {
  @include white-button();
  // color: $black;
  // color: $dark-green;
  border: 1px solid $soft-gray;
  cursor: pointer;
  width: 15vw;
  // border-radius: 0.75rem;
  display: flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
}
</style>