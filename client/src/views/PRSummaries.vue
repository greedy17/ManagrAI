<template>
  <div class="summaries">
    <main id="main">
      <SummariesMainContent @set-summary="setSummary" @set-loader="setLoader" />
    </main>
    <!-- <aside id="right-sidebar">
      <PRRightBar :summary="summary" :summaryLoading="summaryLoading" />
    </aside> -->
  </div>
</template>
<script>
import PRTopBar from '@/components/pr/PRTopBar.vue'
import SummariesMainContent from '@/components/pr/SummariesMainContent.vue'
import PRRightBar from '@/components/pr/PRRightBar.vue'

export default {
  name: 'PRSummaries',
  components: {
    PRTopBar,
    SummariesMainContent,
    PRRightBar,
  },
  data() {
    return {
      summary: null,
      summaryLoading: false,
    }
  },
  watch: {},
  created() {},
  methods: {
    setSummary(sum) {
      this.summary = sum
    },
    setLoader(val) {
      this.summaryLoading = val
      console.log(this.summaryLoading)
    },
  },
  computed: {},
}
</script>

<style lang="scss" scoped>
@import '@/styles/variables';

.summaries {
  background-color: white;
  width: 100vw;
  height: 100vh;
  display: flex;
  font-family: $base-font-family;
  color: $chat-font-color;
  letter-spacing: 0.4px;
  line-height: 1.5;
  position: relative;
}

#main {
  flex: 1;
  width: 100vw;
  background-color: white;
  z-index: 5;
}

.elipsis-text {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  width: 450px;
}

#right-sidebar {
  width: 525px;
  border-left: 1px solid rgba(0, 0, 0, 0.1);
}

// @media (max-width: 1000px) {
//   .summaries {
//     flex-direction: column;
//   }

//   #main {
//     order: 2;
//     width: 100%;
//     height: 75%;
//   }

//   #right-sidebar {
//     width: 100%;
//     height: 40%;
//     order: 1;
//     border-bottom: 1px solid rgba(0, 0, 0, 0.1);
//   }
// }
</style>