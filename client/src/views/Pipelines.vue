<template>
  <div class="pipelines">
    <!-- <div class="pipelines__preview">
      <h1>Hi, {{ user.fullName }}</h1>
      <div style="margin-top: -2rem">
        <h5>
          This is where you can manage your pipeline. All changes will auto sync back to Salesforce
        </h5>
      </div>
    </div> -->

    <div class="pipelines__center">
      <div>
        <div class="spacer"></div>
        <span style="color: #45a16f">Update your pipeline faster</span>
        <h1>Coming Soon.</h1>
        <p style="margin-top: -1rem">
          Email us at mike@mymanagr.com if you have any feedback or questions.
        </p>
        <!-- <div class="connection">
          <img style="height: 2rem" src="@/assets/images/logo.png" />
          <img
            class="filtered-green"
            src="@/assets/images/link.png"
            alt=""
            style="height: 1rem; margin-left: 0.5rem"
          />
          <img
            style="height: 1.5rem; margin-right: 0.5rem"
            src="@/assets/images/salesforce.png"
            alt=""
          />
        </div> -->
      </div>

      <div class="preview-border">
        <img
          src="@/assets/images/pipeline.png"
          style="height: 70vh; width: 50vw; margin-left: 0.5rem"
          alt=""
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Pipelines',
  data() {
    return {}
  },
  computed: {
    user() {
      return this.$store.state.user
    },
  },
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
// @import '@/styles/buttons';

.pipelines {
  margin-top: 3rem;
  color: $base-gray;

  &__preview {
    display: flex;
    align-items: flex-start;
    flex-direction: column;
    margin: 1rem 3rem;
    z-index: 2;
  }
  &__center {
    display: flex;
    align-items: flex-start;
    justify-content: space-evenly;
  }
}

.preview-border {
  box-shadow: 4px 5px 9px $very-light-gray;
  background-color: white;
  margin-top: 2rem;
  border-radius: 0.5rem;
  width: 51vw;
}
.spacer {
  height: 20vh;
}
p {
  font-size: 14px;
}
h1 {
  margin-top: -1px;
  margin-left: -0.1rem;
  font-size: 38px;
}
// .overlay {
//   position: fixed; /* Sit on top of the page content */ /* Hidden by default */
//   z-index: 2; /* Specify a stack order in case you're using a different order for other el background-color: rgba(0, 0, 0, 0.5); /* Black background with opacity */
// }
</style>