<template>
  <div class="summaries">
    <PRTopBar />
    <div class="display-flex">
      <SummariesMainContent />
      <PRRightBar />
    </div>
  </div>
</template>
<script>
import PRTopBar from '@/components/pr/PRTopBar.vue';
import SummariesMainContent from '@/components/pr/SummariesMainContent.vue';
import PRRightBar from '@/components/pr/PRRightBar.vue'

export default {
  name: 'PRSummaries',
  components: {
    PRTopBar,
    SummariesMainContent,
    PRRightBar
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
  .summaries {
    margin-left: 60px;
  }
  .display-flex {
    display: flex;
  }
</style>