import {
  Box,
  Card,
  CardContent,
  Chip,
  Stack,
  Typography,
} from '@mui/material'
import Grid from '@mui/material/GridLegacy'

const researchHighlights = [
  {
    title: 'Market intelligence',
    description:
      'Screen equities across fundamentals, valuation, and momentum metrics to discover actionable insights.',
    chip: 'Coming soon',
  },
  {
    title: 'Sector heatmaps',
    description:
      'Monitor sector rotation and macro trends with interactive performance dashboards.',
    chip: 'Beta',
  },
  {
    title: 'Learning modules',
    description:
      'Strengthen your investing skills with curated lessons, challenges, and real-world case studies.',
    chip: 'In design',
  },
]

export const ResearchPage = () => {
  return (
    <Stack spacing={3}>
      <Box>
        <Typography variant="h4" fontWeight={700} gutterBottom>
          Research & learning hub
        </Typography>
        <Typography color="text.secondary">
          A centralized space for equity research, educational content, and
          macro insights to support informed decisions.
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {researchHighlights.map((item) => (
          <Grid item xs={12} md={4} key={item.title}>
            <Card
              sx={{
                height: '100%',
                background: 'linear-gradient(145deg, #0B1936, #07112B)',
              }}
            >
              <CardContent>
                <Stack spacing={2}>
                  <Chip
                    label={item.chip}
                    variant="outlined"
                    color="secondary"
                    sx={{ alignSelf: 'flex-start' }}
                  />
                  <Typography variant="h6" fontWeight={600}>
                    {item.title}
                  </Typography>
                  <Typography color="text.secondary">
                    {item.description}
                  </Typography>
                </Stack>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Stack>
  )
}

export default ResearchPage
