<template>
  <div>
    <line-chart :chart-data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { Line } from 'vue-chartjs'

export default {
  name: 'ReportLineChart',
  components: {
    LineChart: {
      extends: Line,
      props: ['chartData', 'options'],
      mounted() {
        const ctx = this.$refs.canvas.getContext('2d')
        const gradient = ctx.createLinearGradient(0, 0, 0, 400)

        gradient.addColorStop(0, 'rgba(138, 122, 175, 1)')
        gradient.addColorStop(1, 'rgba(138, 122, 175, 0.3)')

        this.chartData.datasets[0].backgroundColor = gradient

        this.renderChart(this.chartData, this.options)
      },
    },
  },
  data() {
    return {
      chartData: {
        labels: [
          'Jan',
          'Feb',
          'Mar',
          'Apr',
          'May',
          'Jun',
          'Jul',
          'Aug',
          'Sep',
          'Oct',
          'Nov',
          'Dec',
        ],
        datasets: [
          {
            label: 'Performance',
            data: [30, 50, 40, 60, 70, 65, 75, 80, 90, 100, 95, 85],
            borderColor: '#8A7AAF',
            pointBackgroundColor: '#fff',
            pointBorderColor: '#8A7AAF',
            pointHoverBackgroundColor: '#8A7AAF',
            pointHoverBorderColor: '#fff',
            pointRadius: 5,
            pointHoverRadius: 7,
            fill: true,
            lineTension: 0.3, // Smooth curve
          },
        ],
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 1000,
          easing: 'easeInOutQuad',
        },
        legend: {
          display: true,
          labels: {
            fontColor: '#333',
            fontSize: 14,
            padding: 16,
          },
        },
        tooltips: {
          enabled: true,
          mode: 'index',
          intersect: false,
          backgroundColor: 'rgba(0,0,0,0.7)',
          titleFontSize: 14,
          bodyFontSize: 12,
          footerFontSize: 12,
          xPadding: 10,
          yPadding: 10,
          caretSize: 8,
          cornerRadius: 6,
        },
        scales: {
          xAxes: [
            {
              gridLines: {
                display: false,
              },
              ticks: {
                fontColor: '#555',
                fontSize: 12,
                padding: 10,
              },
            },
          ],
          yAxes: [
            {
              gridLines: {
                color: 'rgba(200, 200, 200, 0.2)',
              },
              ticks: {
                beginAtZero: true,
                fontColor: '#555',
                fontSize: 12,
                padding: 10,
              },
            },
          ],
        },
      },
    }
  },
}
</script>

<style scoped>
div {
  position: relative;
  max-width: 100%;
  margin: auto;
  height: 400px;
}
</style>
