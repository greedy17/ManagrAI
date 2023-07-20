<template>
  <div class="clip-report">
    <PRTopBar />
    <div class="display-flex">
      <ClipReportsMainContent />
      <PRRightBar />
    </div>
  </div>
</template>
<script>
import PRTopBar from '@/components/pr/PRTopBar.vue';
import ClipReportsMainContent from '@/components/pr/ClipReportsMainContent.vue';
import PRRightBar from '@/components/pr/PRRightBar.vue'

export default {
  name: 'PRClipReport',
  components: {
    PRTopBar,
    ClipReportsMainContent,
    PRRightBar,
  },
  data() {
    return {

    }
  },
  watch: {

  },
  created() {

  },
  methods: {

  },
  computed: {
    
  }
}
</script>
<style scoped>
  .clip-report {
    margin-left: 60px;
  }
  .display-flex {
    display: flex;
  }
</style>