<template>
  <div class="config">
    <div class="col">
      <h2 style="color: black">Configuring your apps</h2>
      <p style="margin-top: -0.5rem; font-weight: bold; color: #5d5e5e">
        Managr is working it's magic to bring your apps together...
      </p>
    </div>

    <div class="sync">
      <div>
        <div v-if="syncing" class="image_row aligned">
          <img class="synced_images sync_button" src="@/assets/images/salesforce.png" alt="" />
          <img style="height: 2rem" src="@/assets/images/morehoriz.png" alt="" />
          <img class="synced_images sync_button" src="@/assets/images/slackLogo.png" alt="" />
          <img style="height: 2rem" src="@/assets/images/morehoriz.png" alt="" />
          <img class="synced_images sync_button" src="@/assets/images/zoom.png" alt="" />
          <img style="height: 2rem" src="@/assets/images/morehoriz.png" alt="" />
          <img class="synced_images sync_button" src="@/assets/images/gmailCal.png" alt="" />
        </div>

        <!-- <img v-if="syncing" class="sync_button" src="@/assets/images/syncing.png" alt="" /> -->
        <img
          v-if="!syncing"
          class="aligned bounce"
          style="height: 3rem"
          src="@/assets/images/complete.png"
          alt=""
        />

        <!-- <div v-if="syncing" class="image_row">
          <img class="synced_images" src="@/assets/images/zoom.png" alt="" />
          <img style="height: 2rem" src="@/assets/images/morehoriz.png" alt="" />
          <img class="synced_images" src="@/assets/images/gmailCal.png" alt="" />
        </div> -->
      </div>

      <p style="padding-top: 0.75rem" v-if="syncing">Syncing, please wait...</p>
    </div>

    <div v-if="user.isAdmin">
      <button v-if="syncing" class="disabled">Continue</button>
      <button v-else @click="goToUpdate" class="continue_button">Continue</button>
    </div>
    <div v-else>
      <button v-if="syncing" class="disabled">Continue</button>
      <button v-else @click="goToAlerts" class="continue_button">Continue</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Configure',
  data() {
    return {
      syncing: true,
    }
  },
  methods: {
    syncComplete() {
      setTimeout(
        function () {
          this.syncing = !this.syncing
        }.bind(this),
        3000,
      )
    },
    goToUpdate() {
      this.$router.push({ name: 'CustomizeLandingPage' })
    },
    goToAlerts() {
      this.$router.push({ name: 'ListTemplates' })
    },
  },
  computed: {
    user() {
      return this.$store.state.user
    },
  },
  mounted() {
    this.syncComplete()
  },
}
</script>

<style lang='scss' scoped>
@import '@/styles/variables';

.config {
  padding-top: 4rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: white;
  text-align: center;
}

.col {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-top: 1rem;
}

.continue_button {
  height: 2.75rem;
  width: 12rem;
  border-radius: 0.5rem;
  margin: 0rem 0 2rem 0;
  font-size: 1.05rem;
  font-weight: bold;
  color: white;
  background-color: $dark-green;
  border: none;
  cursor: pointer;
}

.disabled {
  background-color: $panther-silver;
  height: 2.75rem;
  width: 12rem;
  border-radius: 0.5rem;
  margin: 0rem 0 2rem 0;
  font-size: 1.05rem;
  color: white;
  border: none;
  cursor: not-allowed;
}

.synced_images {
  height: 3.5rem;
}

.sync {
  background-color: $panther;
  width: 28vw;
  height: 40vh;
  border-radius: 0.5rem;
  margin: 3rem 3rem;
  box-shadow: 3px 4px 7px black;
  color: $panther-silver;
}

.image_row {
  display: flex;
  flex-direction: row;
  justify-content: center;
  align-items: center;
  //   padding-top: 1rem;
  //   padding-left: 6rem;
  //   padding-right: 6rem;
}

@keyframes button-loading-spinner {
  from {
    transform: rotate(0turn);
  }

  to {
    transform: rotate(1turn);
  }
}

.sync_button {
  animation: button-loading-spinner 1s ease infinite;
}
.aligned {
  margin-top: 25%;
  background-repeat: no-repeat;
  background-position: left top;
  -webkit-animation-duration: 1s;
  animation-duration: 1s;
  -webkit-animation-fill-mode: both;
  animation-fill-mode: both;
}

@-webkit-keyframes bounce {
  0%,
  20%,
  50%,
  80%,
  100% {
    -webkit-transform: translateY(0);
  }
  40% {
    -webkit-transform: translateY(-30px);
  }
  60% {
    -webkit-transform: translateY(-15px);
  }
}

@keyframes bounce {
  0%,
  20%,
  50%,
  80%,
  100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-30px);
  }
  60% {
    transform: translateY(-15px);
  }
}

.bounce {
  -webkit-animation-name: bounce;
  animation-name: bounce;
}
</style>