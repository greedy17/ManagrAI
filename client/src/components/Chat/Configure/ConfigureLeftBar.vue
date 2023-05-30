<template>
  <div class="content-and-logout-container">
    <div class="content-container">
      <div class="img-container">
        <img src="@/assets/images/logo.png" height="40px" />
      </div>
      <h4>Configure</h4>
      <div>
        <div>
          <p>Integrations</p>
        </div>
        <div>
          <p>Forms</p>
        </div>
        <div>
          <p>Workflow</p>
        </div>
        <div>
          <p>Note Templates</p>
        </div>
        <div>
          <p>Meetings</p>
        </div>
        <div>
          <p>Profile</p>
        </div>
      </div>
    </div>
    <div>
      <div>
        <p>Demo Center</p>
      </div>
      <div>
        <p><img src="@/assets/images/logout.svg" height="14px" style="margin-right: 0.5rem;" />Log out</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfigureLeftBar',
  props: {

  },
  data() {
    return {

    }
  }
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';
@import '@/styles/buttons';
@import '@/styles/cards';
@import '@/styles/mixins/utils';
@import '@/styles/mixins/inputs';
@import '@/styles/modals';

.content-and-logout-container {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  height: 90vh;
}
.content-container {
  margin-top: 1rem;
}
.img-container {
  display: flex;
  justify-content: center;
}
</style>